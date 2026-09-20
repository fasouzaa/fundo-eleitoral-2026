import { readFile } from "fs/promises";
import path from "path";
import type { CriteriosFile } from "./types-criterios";
import type { CandidatosFile, Summary } from "./types";

const dataDir = path.join(process.cwd(), "public", "data");

export async function getSummary(): Promise<Summary> {
  const raw = await readFile(path.join(dataDir, "summary.json"), "utf-8");
  return JSON.parse(raw) as Summary;
}

export async function getCandidatos(): Promise<CandidatosFile> {
  const raw = await readFile(path.join(dataDir, "candidatos.json"), "utf-8");
  return JSON.parse(raw) as CandidatosFile;
}

export async function getCriterios(): Promise<CriteriosFile> {
  const raw = await readFile(path.join(dataDir, "criterios.json"), "utf-8");
  return JSON.parse(raw) as CriteriosFile;
}
