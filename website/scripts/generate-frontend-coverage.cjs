const fs = require('fs');
const path = require('path');
const v8toIstanbul = require('v8-to-istanbul');
const { createCoverageMap } = require('istanbul-lib-coverage');
const libReport = require('istanbul-lib-report');
const reports = require('istanbul-reports');

const WEBSITE_ROOT = path.resolve(__dirname, '..');
const FRONTEND_REPORT_DIR = path.resolve(__dirname, '..', '..', 'reports', 'frontend');
const RAW_COVERAGE_DIR = path.join(FRONTEND_REPORT_DIR, '.raw-coverage');
const OUTPUT_DIR = path.join(FRONTEND_REPORT_DIR, 'js-coverage');

function toLocalFile(url) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== '127.0.0.1' && parsed.hostname !== 'localhost') {
      return null;
    }

    const pathname = parsed.pathname || '';
    if (!pathname.startsWith('/js/') || !pathname.endsWith('.js')) {
      return null;
    }

    const localPath = path.resolve(WEBSITE_ROOT, `.${pathname}`);
    if (!fs.existsSync(localPath)) {
      return null;
    }

    return localPath;
  } catch {
    return null;
  }
}

async function convertScriptCoverage(scriptCoverage, coverageMap) {
  const localFile = toLocalFile(scriptCoverage.url);
  if (!localFile || !Array.isArray(scriptCoverage.functions)) {
    return;
  }

  const source = fs.readFileSync(localFile, 'utf8');
  const converter = v8toIstanbul(localFile, 0, { source });
  await converter.load();
  converter.applyCoverage(scriptCoverage.functions);
  coverageMap.merge(converter.toIstanbul());
}

async function buildCoverage() {
  if (!fs.existsSync(RAW_COVERAGE_DIR)) {
    console.log('No raw frontend coverage found. Run `npm run test:e2e:coverage` first.');
    process.exit(0);
  }

  const files = fs
    .readdirSync(RAW_COVERAGE_DIR)
    .filter((name) => name.endsWith('.json'))
    .map((name) => path.join(RAW_COVERAGE_DIR, name));

  if (files.length === 0) {
    console.log('No raw frontend coverage files to process.');
    process.exit(0);
  }

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const coverageMap = createCoverageMap({});

  for (const filePath of files) {
    const payload = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const scripts = Array.isArray(payload.scripts) ? payload.scripts : [];

    for (const scriptCoverage of scripts) {
      await convertScriptCoverage(scriptCoverage, coverageMap);
    }
  }

  if (coverageMap.files().length === 0) {
    console.log('No website /js/*.js coverage entries were collected.');
    process.exit(0);
  }

  const context = libReport.createContext({
    dir: OUTPUT_DIR,
    coverageMap,
  });

  reports.create('html').execute(context);
  reports.create('lcovonly', { file: 'lcov.info' }).execute(context);
  reports.create('json-summary', { file: 'coverage-summary.json' }).execute(context);
  reports.create('text-summary').execute(context);

  const summary = coverageMap.getCoverageSummary().toJSON();
  fs.writeFileSync(path.join(OUTPUT_DIR, 'coverage-summary-full.json'), JSON.stringify(summary, null, 2), 'utf8');

  console.log(`Frontend JS coverage generated in ${OUTPUT_DIR}`);
}

buildCoverage().catch((error) => {
  console.error('Failed to generate frontend JS coverage:', error);
  process.exit(1);
});
