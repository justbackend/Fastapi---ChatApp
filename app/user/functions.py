import json
from datetime import timedelta, datetime

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import create_access_token
from app.config import settings
from app.exceptions import CustomException
from app.response import CustomResponse, PostResponse, restricted_response, success_response
from app.user.models import User
from app.user.schemas import PersonalInfoUpdate, LegalInfoCreate
from app.utils.queries import get_one_object, get_or_404


async def register(form, db):
    # user = db.query(User).filter(User.username == form.username).first()
    #
    # if user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    #
    # user = User(username=form.username, password=hashed_password)
    # db.add(user)
    # db.commit()
    # db.refresh(user)
    #
    # access_token = await create_access_token({'id': user.id})
    return 'hi'


async def verify_phone_number_f(form, request, db):
    cache = request.app.redis
    phone_number = form.phone_number
    await cache.set(phone_number, 123456, 5 * 60)

    user = await get_one_object(db, User, phone_number=phone_number)

    if user and user.is_active:
        return CustomResponse(message="Tasdiqlash ko'di yuborildi")
    return CustomResponse(message="Tasdiqlash ko'di yuborildi", status_code=201)


async def verify_sms_code_f(db, form, request):
    cache = request.app.redis
    code = await cache.get(form.phone_number)
    if not code:
        raise CustomException("Code ni amal qilish muddati tugagan")

    code = int(code)

    if code != form.code:
        raise CustomException("Kiritilgan code noto'g'ri")

    user = await get_one_object(db, User, phone_number=form.phone_number)
    if user:
        access_token = await create_access_token(data={'sub': user.phone_number},
                                                 expires_delta=timedelta(days=(365 * 5)))
        data = {"access_token": access_token, "token_type": "bearer"}
        return CustomResponse(content=data)

    new_user = User(**form.model_dump(exclude=['code']))
    await new_user.save(db)
    access_token = await create_access_token(data={'sub': new_user.phone_number},
                                             expires_delta=timedelta(days=(365 * 5)))
    data = {"access_token": access_token, "token_type": "bearer"}
    await cache.delete(form.phone_number)
    return CustomResponse(content=data, status_code=201)


async def get_personal_info_f(current_user, db):
    query = select(User).where(User.id==current_user.id).options(selectinload(User.profile), selectinload(User.legal_info))
    info = await db.execute(query)
    return info.scalars().first()


async def update_personal_info_f(current_user, db, form: PersonalInfoUpdate):
    profile = await get_or_404(db, Profile, user=current_user)
    await profile.update(db, **form.model_dump(exclude_none=True))
    return current_user


async def activate_user_f(form, current_user, db):
    # if current_user.is_active:
    #     raise restricted_response

    url = "https://devmyid.uz/api/v1/oauth2/access-token"

    data = {
        "grant_type": "authorization_code",
        "code": form.code,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail="Error fetching access token")

        response_data = json.loads(response.text)
        token = response_data.get('access_token')
        if not token:
            raise HTTPException(status_code=400, detail="Access token not found in the response")

        url2 = "https://devmyid.uz/api/v1/users/me"
        headers2 = {
            "Authorization": f"Bearer {token}"
        }

        response2 = await client.get(url2, headers=headers2)
        if response2.status_code != 200:
            raise HTTPException(status_code=response2.status_code, detail="Error fetching user information")
        # null = None
        # user_info = {
        #     "profile": {
        #         "common_data": {
        #             "first_name": "JALOLXON",
        #             "first_name_en": "JALOLKHON",
        #             "middle_name": "JA’FARXON O‘G‘LI",
        #             "last_name": "KAMOLXONOV",
        #             "last_name_en": "KAMOLKHONOV",
        #             "pinfl": "53012027080039",
        #             "gender": "1",
        #             "birth_place": "MARG‘ILON SHAHRI",
        #             "birth_country": "УЗБЕКИСТАН",
        #             "birth_country_id": "182",
        #             "birth_country_id_cbu": "860",
        #             "birth_date": "30.12.2002",
        #             "nationality": "УЗБЕК/УЗБЕЧКА",
        #             "nationality_id": "44",
        #             "nationality_id_cbu": "01",
        #             "citizenship": "УЗБЕКИСТАН",
        #             "citizenship_id": "182",
        #             "citizenship_id_cbu": "860",
        #             "doc_type": "БИОМЕТРИЧЕСКИЙ ПАСПОРТ ГРАЖДАНИНА РЕСПУБЛИКИ УЗБЕКИСТАН",
        #             "doc_type_id": "46",
        #             "doc_type_id_cbu": "6",
        #             "sdk_hash": "fe0435c0a8d39bd3ad97f455db1ad640",
        #             "last_update_pass_data": "2024-08-14T10:39:01.778433+00:00",
        #             "last_update_address": "2024-08-14T10:39:02.734336+00:00"
        #         },
        #         "doc_data": {
        #             "pass_data": "AC2324043",
        #             "issued_by": "МАРГИЛАНСКИЙ ГОВД ФЕРГАНСКОЙ ОБЛАСТИ",
        #             "issued_by_id": "30412",
        #             "issued_date": "19.10.2019",
        #             "expiry_date": "18.10.2029",
        #             "doc_type": "БИОМЕТРИЧЕСКИЙ ПАСПОРТ ГРАЖДАНИНА РЕСПУБЛИКИ УЗБЕКИСТАН",
        #             "doc_type_id": "46",
        #             "doc_type_id_cbu": "6"
        #         },
        #         "contacts": {
        #             "phone": null,
        #             "email": null
        #         },
        #         "address": {
        #             "permanent_address": "ГУРАВВАЛ МФЙ, ШИФОКОР КЎЧАСИ,  uy:15",
        #             "temporary_address": null,
        #             "permanent_registration": {
        #                 "region": "ФАРҒОНА ВИЛОЯТИ",
        #                 "address": "ГУРАВВАЛ МФЙ, ШИФОКОР КЎЧАСИ,  uy:15",
        #                 "country": "ЎЗБЕКИСТОН",
        #                 "cadastre": "15:19:01:02:01:0492",
        #                 "district": "МАРҒИЛОН ШАҲРИ",
        #                 "region_id": "15",
        #                 "country_id": "182",
        #                 "district_id": "1520",
        #                 "region_id_cbu": "30",
        #                 "country_id_cbu": "860",
        #                 "district_id_cbu": "149",
        #                 "registration_date": "2019-11-01T00:00:00"
        #             },
        #             "temporary_registration": null
        #         },
        #         "authentication_method": "strong"
        #     }
        # }
        user_info = response2.json()
        common_data = user_info['profile']['common_data']
        address = user_info['profile']['address']
        birth_date = datetime.strptime(common_data['birth_date'], "%d.%m.%Y").date()

        profile_data = {
            'user_id': current_user.id,
            'first_name': common_data['first_name'],
            'last_name': common_data['last_name'],
            'birth_place': common_data['birth_place'],
            'birth_date': birth_date,
            'address': address['permanent_address'],
            'pinfl': int(common_data['pinfl']),
        }

        profile = Profile(**profile_data)
        await profile.save(db)
        current_user.is_legal = form.is_legal
        if not form.is_legal:
            current_user.is_active = True
        await db.commit()
        return profile


async def create_legal_info_f(current_user, form: LegalInfoCreate, db):
    legal_info = LegalInfo(user_id=current_user.id, **form.model_dump())
    await legal_info.save(db)
    return legal_info


async def get_unactive_users_f(db):
    query = select(User).join(User.legal_info).join(User.profile).where(User.is_legal == True).options(selectinload(User.legal_info))
    result = await db.execute(query)
    return result.scalars().all()


async def activate_legal_user_f(db, user_id):
    query = select(User).join(User.legal_info).join(User.profile).where(User.is_legal == True).options(
        selectinload(User.legal_info))
    result = await db.execute(query)
    user =  result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Foydalanuvchi aktivlash uchun tayyor emas")
    user.is_active = True
    await db.commit()
    return success_response

async def my_status_f(current_user, db):
    is_registered = True if await get_one_object(db, Profile, user=current_user) else False
    user_info = {
        'is_active': current_user.is_active,
        'is_registered': is_registered
    }

    return user_info