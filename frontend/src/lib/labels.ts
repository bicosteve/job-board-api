/** DB stores encoded strings for jobs; map for display */
export function employmentLabel(code: string | number | undefined | null): string {
  const v = String(code ?? "");
  const map: Record<string, string> = {
    "1": "Full time",
    "2": "Part time",
    "3": "Contract",
    "4": "Internship",
  };
  return (map[v] ?? v) || "—";
}

export function jobStatusLabel(code: string | number | undefined | null): string {
  const v = String(code ?? "");
  const map: Record<string, string> = {
    "5": "Open",
    "6": "Closed",
    "7": "Draft",
  };
  return (map[v] ?? v) || "—";
}

export const APPLICATION_STATUS_OPTIONS = [
  { value: 1, label: "Submitted" },
  { value: 2, label: "In review" },
  { value: 3, label: "Interview" },
  { value: 4, label: "Decision" },
] as const;

export function applicationStatusLabel(n: number | string | undefined): string {
  const v = Number(n);
  const found = APPLICATION_STATUS_OPTIONS.find((x) => x.value === v);
  return found?.label ?? String(n ?? "—");
}
