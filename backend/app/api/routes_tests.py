"""Test case execution API endpoints for the 4 Mandatory Official Test Cases."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.schemas import TestCaseResult
from backend.app.services.test_runner import OfficialTestCaseRunner

router = APIRouter(prefix="/tests", tags=["Official Test Suite"])


@router.get("", response_model=List[TestCaseResult])
def list_test_definitions():
    """Get the four mandatory test cases and their specifications."""
    # Run the tests to show current verified state
    results = OfficialTestCaseRunner.run_all()
    return [TestCaseResult(**r) for r in results]


@router.post("/{test_case_id}/run", response_model=TestCaseResult)
def run_single_test_case(test_case_id: str, db: Session = Depends(get_db)):
    """Run an individual official test case with live assertions."""
    t_id = test_case_id.upper()
    if t_id == "TC1":
        res = OfficialTestCaseRunner.run_tc1(db)
    elif t_id == "TC2":
        res = OfficialTestCaseRunner.run_tc2(db)
    elif t_id == "TC3":
        res = OfficialTestCaseRunner.run_tc3(db)
    elif t_id == "TC4":
        res = OfficialTestCaseRunner.run_tc4(db)
    else:
        raise HTTPException(status_code=404, detail=f"Test case '{test_case_id}' not found. Valid: TC1, TC2, TC3, TC4")

    return TestCaseResult(**res)


@router.post("/run-all", response_model=List[TestCaseResult])
def run_all_tests(db: Session = Depends(get_db)):
    """Execute all four mandatory official test cases sequentially and return audited results."""
    results = OfficialTestCaseRunner.run_all(db)
    return [TestCaseResult(**r) for r in results]
