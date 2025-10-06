from fastapi import APIRouter

router = APIRouter(prefix="/home", tags=["home"])


# router.get("/", response_class=ItemsPublic)
