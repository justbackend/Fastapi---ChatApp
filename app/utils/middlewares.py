from fastapi import Request, Response


from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse


async def handle_integrity_errors(request, call_next):
    try:
        response = await call_next(request)
        return response
    except IntegrityError as e:
        error_msg = str(e.orig)
        error_code = error_msg.split("(")[1].split(",")[0].strip()
        if error_code == '1062':
            return JSONResponse({'detail': "Bu ma'lumot bazada mavjud!"}, status_code=400)
        elif error_code == '1452':
            return JSONResponse({'detail': "Bu ma'lumot bazada mavjud emaslik xatoligi bor!"}, status_code=400)
        else:
            return JSONResponse({'detail': "Ko'zda tutilmagan xatolik!"}, status_code=400)