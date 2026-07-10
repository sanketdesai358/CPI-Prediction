import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(root, "src", "data");
const backupDir = path.join(root, ".private-data-backup");
const nextDir = path.join(root, ".next");
const nextCli = path.join(root, "node_modules", "next", "dist", "bin", "next");

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed with exit ${result.status}`);
  }
}

function copyDir(from, to) {
  if (fs.existsSync(to)) fs.rmSync(to, { recursive: true, force: true });
  fs.cpSync(from, to, { recursive: true });
}

function removeDirIfPossible(dir) {
  if (!fs.existsSync(dir)) return;
  if (!process.env.VERCEL && !process.env.CI) return;
  try {
    fs.rmSync(dir, { recursive: true, force: true, maxRetries: 10, retryDelay: 250 });
  } catch (error) {
    throw error;
  }
}

try {
  copyDir(dataDir, backupDir);
  run("python", ["scripts/sanitize-public-data.py", "--in-place"]);
  removeDirIfPossible(nextDir);
  run(process.execPath, [nextCli, "build"]);
} finally {
  if (fs.existsSync(backupDir)) {
    copyDir(backupDir, dataDir);
    fs.rmSync(backupDir, { recursive: true, force: true });
  }
}
