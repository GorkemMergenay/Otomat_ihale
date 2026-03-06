from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.models.keyword_rule import KeywordRule
from app.schemas.keyword_rule import KeywordRuleCreate, KeywordRuleRead, KeywordRuleUpdate

router = APIRouter(prefix="/keyword-rules", tags=["keyword-rules"])


@router.get("", response_model=list[KeywordRuleRead])
def list_keyword_rules(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[KeywordRuleRead]:
    rows = db.scalars(select(KeywordRule).order_by(KeywordRule.category.asc(), KeywordRule.keyword.asc())).all()
    return [KeywordRuleRead.model_validate(row) for row in rows]


@router.post("", response_model=KeywordRuleRead, status_code=status.HTTP_201_CREATED)
def create_keyword_rule(
    payload: KeywordRuleCreate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> KeywordRuleRead:
    row = KeywordRule(**payload.model_dump(mode="json"))
    db.add(row)
    db.commit()
    db.refresh(row)
    return KeywordRuleRead.model_validate(row)


@router.patch("/{rule_id}", response_model=KeywordRuleRead)
def update_keyword_rule(
    rule_id: int,
    payload: KeywordRuleUpdate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> KeywordRuleRead:
    row = db.get(KeywordRule, rule_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anahtar kelime kuralı bulunamadı")

    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(row, key, value)

    db.add(row)
    db.commit()
    db.refresh(row)
    return KeywordRuleRead.model_validate(row)


@router.delete("/{rule_id}", status_code=status.HTTP_200_OK)
def delete_keyword_rule(
    rule_id: int,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    row = db.get(KeywordRule, rule_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anahtar kelime kuralı bulunamadı")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}
