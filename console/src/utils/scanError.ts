import type { SecurityScanErrorResponse } from '../api/modules/security';

// [hanbao modification] Skill scanner removed. These functions are kept as
// no-op stubs so that Skills page code that referenced the security scanner
// still compiles and behaves as if "no scan warnings, no scan errors".

export const catchErrorByCode = (
  code: string,
  fn: (err: SecurityScanErrorResponse) => void,
) => fn({ type: 'security_scan_failed', message: code } as SecurityScanErrorResponse);

export const isSecurityScanError = (
  _err: unknown,
): _err is SecurityScanErrorResponse => false;

export const classifySecurityScanError = (
  _err: SecurityScanErrorResponse,
): string => 'error';

export const getSecurityScanErrorMessage = (
  err: SecurityScanErrorResponse,
): string => err.message;

export const handleScanError = (_err: unknown, _t: unknown): boolean => false;

export const checkScanWarnings = (
  _skillName: string,
  _getBlockedHistory: unknown,
  _getSkillScanner: unknown,
  _t: unknown,
): { passed: boolean; warnings: unknown[] } => ({ passed: true, warnings: [] });

export const showScanErrorModal = (_err: unknown, _t?: unknown): void => {};
