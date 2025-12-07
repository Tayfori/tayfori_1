"""
Gönüllü Eşleştirme Algoritması

Bu algoritma, bir afet çağrısı için en uygun gönüllüleri bulur.
Skorlama kriterleri:
- Yetkinlik eşleşmesi: %40
- Uzaklık (konum): %30
- Rating (değerlendirme): %20
- Deneyim: %10
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Tuple, Optional
from ..models.volunteer import Volunteer, VolunteerStatus, volunteer_skills
from ..models.disaster_call import DisasterCall, DisasterCallSkill
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)


class VolunteerMatchingAlgorithm:
    """Gönüllü eşleştirme algoritması"""

    # Ağırlıklar
    SKILL_WEIGHT = 0.40  # Yetkinlik eşleşmesi
    DISTANCE_WEIGHT = 0.30  # Uzaklık
    RATING_WEIGHT = 0.20  # Değerlendirme
    EXPERIENCE_WEIGHT = 0.10  # Deneyim

    # Mesafe sabitleri
    EARTH_RADIUS_KM = 6371.0  # Dünya yarıçapı (km)

    def __init__(self, db: Session):
        self.db = db

    def find_best_matches(
        self,
        disaster_call_id: int,
        max_distance_km: float = 50.0,
        limit: Optional[int] = None
    ) -> List[Tuple[Volunteer, float, float]]:
        """
        Bir afet çağrısı için en uygun gönüllüleri bulur.

        Args:
            disaster_call_id: Afet çağrısı ID
            max_distance_km: Maksimum mesafe (km)
            limit: Maksimum gönüllü sayısı (None ise sınırsız)

        Returns:
            List of (volunteer, match_score, distance_km)
        """
        # Afet çağrısını al
        disaster_call = self.db.query(DisasterCall).filter(
            DisasterCall.id == disaster_call_id
        ).first()

        if not disaster_call:
            logger.error(f"Disaster call {disaster_call_id} not found")
            return []

        # Gerekli yetkinlikleri al
        required_skills = self.db.query(DisasterCallSkill).filter(
            DisasterCallSkill.disaster_call_id == disaster_call_id
        ).all()

        # Müsait gönüllüleri al
        available_volunteers = self.db.query(Volunteer).filter(
            and_(
                Volunteer.is_approved == True,
                Volunteer.status.in_([VolunteerStatus.ACTIVE]),
                Volunteer.notification_enabled == True
            )
        ).all()

        logger.info(f"Found {len(available_volunteers)} available volunteers")

        # Her gönüllü için skor hesapla
        scored_volunteers = []
        for volunteer in available_volunteers:
            # Skor hesapla
            score, distance = self._calculate_match_score(
                volunteer,
                disaster_call,
                required_skills,
                max_distance_km
            )

            # Mesafe kontrolü
            if distance is not None and distance > max_distance_km:
                continue

            if score > 0:
                scored_volunteers.append((volunteer, score, distance))

        # Skora göre sırala (yüksekten düşüğe)
        scored_volunteers.sort(key=lambda x: x[1], reverse=True)

        # Limit uygula
        if limit:
            scored_volunteers = scored_volunteers[:limit]

        logger.info(f"Matched {len(scored_volunteers)} volunteers for disaster call {disaster_call_id}")

        return scored_volunteers

    def _calculate_match_score(
        self,
        volunteer: Volunteer,
        disaster_call: DisasterCall,
        required_skills: List[DisasterCallSkill],
        max_distance_km: float
    ) -> Tuple[float, Optional[float]]:
        """
        Bir gönüllü için toplam eşleşme skoru hesaplar.

        Returns:
            (match_score, distance_km)
        """
        # 1. Yetkinlik skoru
        skill_score = self._calculate_skill_score(volunteer, required_skills)

        # 2. Mesafe skoru
        distance_km = None
        distance_score = 0.0

        if disaster_call.latitude and disaster_call.longitude:
            if volunteer.latitude and volunteer.longitude:
                distance_km = self._calculate_distance(
                    volunteer.latitude,
                    volunteer.longitude,
                    disaster_call.latitude,
                    disaster_call.longitude
                )
                distance_score = self._calculate_distance_score(distance_km, max_distance_km)
            else:
                # Konum bilgisi yoksa orta skor ver
                distance_score = 0.5
        else:
            # Afet konumu yoksa mesafe skoru verme
            distance_score = 0.5

        # 3. Rating skoru (0-5 -> 0-1)
        rating_score = volunteer.rating / 5.0

        # 4. Deneyim skoru
        experience_score = self._calculate_experience_score(volunteer)

        # Toplam skor hesapla (0-100 arası)
        total_score = (
            skill_score * self.SKILL_WEIGHT +
            distance_score * self.DISTANCE_WEIGHT +
            rating_score * self.RATING_WEIGHT +
            experience_score * self.EXPERIENCE_WEIGHT
        ) * 100

        return total_score, distance_km

    def _calculate_skill_score(
        self,
        volunteer: Volunteer,
        required_skills: List[DisasterCallSkill]
    ) -> float:
        """
        Yetkinlik eşleşme skoru hesaplar (0-1 arası).
        """
        if not required_skills:
            return 1.0  # Yetkinlik gereksinimi yoksa tam skor

        # Gönüllünün yetkinliklerini al
        volunteer_skill_ids = {skill.id for skill in volunteer.skills}

        # Gönüllünün yetkinlik seviyelerini al
        volunteer_skill_levels = {}
        result = self.db.query(
            volunteer_skills.c.skill_id,
            volunteer_skills.c.proficiency_level,
            volunteer_skills.c.certified
        ).filter(
            volunteer_skills.c.volunteer_id == volunteer.id
        ).all()

        for skill_id, level, certified in result:
            volunteer_skill_levels[skill_id] = {
                'level': level,
                'certified': certified
            }

        total_score = 0.0
        total_weight = 0.0

        for req_skill in required_skills:
            # Ağırlık (mandatory ise daha yüksek)
            weight = 2.0 if req_skill.is_mandatory else 1.0
            total_weight += weight

            # Gönüllünün bu yetkinliği var mı?
            if req_skill.skill_id in volunteer_skill_ids:
                skill_info = volunteer_skill_levels.get(req_skill.skill_id, {})
                vol_level = skill_info.get('level', 1)
                is_certified = skill_info.get('certified', False)

                # Seviye kontrolü
                if vol_level >= req_skill.min_proficiency:
                    # Tam skor
                    skill_score = 1.0

                    # Sertifikalı ise bonus
                    if is_certified:
                        skill_score = 1.2

                    # Seviye fazlaysa bonus
                    level_bonus = (vol_level - req_skill.min_proficiency) * 0.1
                    skill_score += level_bonus

                    total_score += min(skill_score, 1.5) * weight
                else:
                    # Seviye yetersiz ama yetkinlik var
                    total_score += 0.3 * weight
            else:
                # Yetkinlik yok
                if req_skill.is_mandatory:
                    # Zorunlu yetkinlik yoksa 0 skor
                    return 0.0
                else:
                    # Opsiyonel, biraz ceza
                    total_score += 0.0

        return total_score / total_weight if total_weight > 0 else 0.0

    def _calculate_distance_score(self, distance_km: float, max_distance_km: float) -> float:
        """
        Mesafe skoru hesaplar (0-1 arası).
        Yakın mesafe = yüksek skor
        """
        if distance_km <= 0:
            return 1.0

        # Lineer azalma (max mesafede 0, 0 mesafede 1)
        score = 1.0 - (distance_km / max_distance_km)
        return max(0.0, min(1.0, score))

    def _calculate_experience_score(self, volunteer: Volunteer) -> float:
        """
        Deneyim skoru hesaplar (0-1 arası).
        """
        # Tamamlanan görev sayısına göre
        completed = volunteer.completed_missions

        if completed == 0:
            return 0.2  # Yeni gönüllüler için temel skor
        elif completed < 5:
            return 0.4
        elif completed < 10:
            return 0.6
        elif completed < 20:
            return 0.8
        else:
            return 1.0

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        İki nokta arasındaki mesafeyi Haversine formülü ile hesaplar (km).
        """
        # Dereceyi radyana çevir
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        # Farklar
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formülü
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = self.EARTH_RADIUS_KM * c

        return distance

    def get_volunteer_details_for_skill(
        self,
        skill_id: int,
        min_proficiency: int = 1,
        max_distance_km: Optional[float] = None,
        center_lat: Optional[float] = None,
        center_lon: Optional[float] = None,
        limit: int = 100
    ) -> List[Tuple[Volunteer, float]]:
        """
        Belirli bir yetkinliğe sahip gönüllüleri getirir.

        Returns:
            List of (volunteer, proficiency_level)
        """
        # Yetkinliğe sahip gönüllüleri al
        query = self.db.query(Volunteer).join(
            volunteer_skills,
            Volunteer.id == volunteer_skills.c.volunteer_id
        ).filter(
            and_(
                volunteer_skills.c.skill_id == skill_id,
                volunteer_skills.c.proficiency_level >= min_proficiency,
                Volunteer.is_approved == True,
                Volunteer.status == VolunteerStatus.ACTIVE
            )
        )

        volunteers = query.all()

        # Mesafe filtresi
        if max_distance_km and center_lat and center_lon:
            filtered = []
            for vol in volunteers:
                if vol.latitude and vol.longitude:
                    distance = self._calculate_distance(
                        vol.latitude, vol.longitude,
                        center_lat, center_lon
                    )
                    if distance <= max_distance_km:
                        # Yetkinlik seviyesini al
                        level = self.db.query(volunteer_skills.c.proficiency_level).filter(
                            and_(
                                volunteer_skills.c.volunteer_id == vol.id,
                                volunteer_skills.c.skill_id == skill_id
                            )
                        ).scalar()
                        filtered.append((vol, level or 1))
            volunteers = filtered
        else:
            # Seviye bilgisi ekle
            result = []
            for vol in volunteers:
                level = self.db.query(volunteer_skills.c.proficiency_level).filter(
                    and_(
                        volunteer_skills.c.volunteer_id == vol.id,
                        volunteer_skills.c.skill_id == skill_id
                    )
                ).scalar()
                result.append((vol, level or 1))
            volunteers = result

        return volunteers[:limit]
