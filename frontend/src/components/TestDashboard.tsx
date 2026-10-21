import React, { useState } from 'react';
import { Language, TestCaseResult } from '../types';
import { translations } from '../i18n/translations';
import { api } from '../services/api';
import {
  CheckCircle2,
  XCircle,
  Play,
  RotateCcw,
  ShieldCheck,
  Check,
  FileCode,
  Clock,
} from 'lucide-react';

interface TestDashboardProps {
  testCases: TestCaseResult[];
  language: Language;
  onRefreshTests: () => void;
}

export const TestDashboard: React.FC<TestDashboardProps> = ({
  testCases,
  language,
  onRefreshTests,
}) => {
  const t = translations[language];

  const [runningId, setRunningId] = useState<string | null>(null);
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [activeResults, setActiveResults] = useState<Record<string, TestCaseResult>>(() => {
    const init: Record<string, TestCaseResult> = {};
    testCases.forEach((tc) => {
      init[tc.test_case_id] = tc;
    });
    return init;
  });

  const handleRunSingle = async (testCaseId: string) => {
    setRunningId(testCaseId);
    try {
      const res = await api.runSingleTest(testCaseId);
      setActiveResults((prev) => ({ ...prev, [testCaseId]: res }));
      onRefreshTests();
    } catch (e) {
      console.error(e);
    } finally {
      setRunningId(null);
    }
  };

  const handleRunAll = async () => {
    setIsRunningAll(true);
    try {
      const results = await api.runAllTests();
      const updated: Record<string, TestCaseResult> = {};
      results.forEach((r) => {
        updated[r.test_case_id] = r;
      });
      setActiveResults(updated);
      onRefreshTests();
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunningAll(false);
    }
  };

  const allPassed =
    Object.values(activeResults).length > 0 &&
    Object.values(activeResults).every((tc) => tc.status === 'passed');

  return (
    <div className="test-dashboard-container panel">
      {/* Header */}
      <div className="panel-header">
        <div>
          <div className="title-with-badge">
            <h2 className="panel-title">{t.testsTitle}</h2>
            {allPassed && (
              <span className="tests-all-pass-badge">
                <CheckCircle2 size={16} /> All 4 Test Cases Passing
              </span>
            )}
          </div>
          <p className="panel-subtitle">{t.testsSubtitle}</p>
        </div>

        <button
          className="btn-primary-large"
          onClick={handleRunAll}
          disabled={isRunningAll || runningId !== null}
        >
          {isRunningAll ? (
            <>
              <RotateCcw size={18} className="spin" />
              <span>Running All Tests...</span>
            </>
          ) : (
            <>
              <Play size={18} />
              <span>{t.btnRunAllTests}</span>
            </>
          )}
        </button>
      </div>

      {/* Test Cases Cards */}
      <div className="test-cases-stack">
        {['TC1', 'TC2', 'TC3', 'TC4'].map((tcId) => {
          const item = activeResults[tcId];
          if (!item) return null;

          const isPassing = item.status === 'passed';
          const isThisRunning = runningId === tcId;

          return (
            <div
              key={tcId}
              className={`test-case-card ${isPassing ? 'test-passed' : 'test-failed'}`}
            >
              <div className="tc-header-row">
                <div className="tc-title-group">
                  <span className="tc-badge">{item.test_case_id}</span>
                  <h3 className="tc-title">{item.title}</h3>
                </div>

                <div className="tc-status-actions">
                  <div className={`tc-status-pill ${item.status}`}>
                    {isPassing ? (
                      <>
                        <CheckCircle2 size={16} /> <span>{t.testPassed}</span>
                      </>
                    ) : (
                      <>
                        <XCircle size={16} /> <span>{t.testFailed}</span>
                      </>
                    )}
                  </div>
                  <span className="tc-duration">
                    <Clock size={12} /> {item.duration_ms} ms
                  </span>
                  <button
                    className="btn-tc-run"
                    onClick={() => handleRunSingle(item.test_case_id)}
                    disabled={isThisRunning || isRunningAll}
                  >
                    {isThisRunning ? (
                      <RotateCcw size={14} className="spin" />
                    ) : (
                      <Play size={14} />
                    )}
                    <span>{isThisRunning ? 'Testing...' : t.btnRunTest}</span>
                  </button>
                </div>
              </div>

              {/* Assertions List */}
              <div className="tc-assertions-block">
                <span className="tc-block-head">Automated Assertions Verified:</span>
                <ul className="assertions-list">
                  {item.assertions_passed.map((pass, i) => (
                    <li key={i} className="assert-item pass">
                      <Check size={14} color="#2e7d32" />
                      <span>{pass}</span>
                    </li>
                  ))}
                  {item.assertions_failed.map((fail, i) => (
                    <li key={i} className="assert-item fail">
                      <XCircle size={14} color="#c62828" />
                      <span>{fail}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Input Fixture vs Actual Output Collapsible */}
              <details className="tc-details-collapsible">
                <summary>
                  <FileCode size={14} /> Inspect Fixture, Expectations & Output Trace
                </summary>
                <div className="tc-json-grid">
                  <div className="json-column">
                    <span className="json-col-title">Input Fixture:</span>
                    <pre>{JSON.stringify(item.input_fixture, null, 2)}</pre>
                  </div>
                  <div className="json-column">
                    <span className="json-col-title">Expected Behavior:</span>
                    <pre>{JSON.stringify(item.expected_behavior, null, 2)}</pre>
                  </div>
                  <div className="json-column">
                    <span className="json-col-title">Actual Evaluated Output:</span>
                    <pre>{JSON.stringify(item.actual_output, null, 2)}</pre>
                  </div>
                </div>
              </details>
            </div>
          );
        })}
      </div>
    </div>
  );
};
