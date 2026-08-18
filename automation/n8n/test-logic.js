// Harness that mimics the n8n Code-node runtime so the two Code nodes can be
// exercised against the real CSV before anything is wired to SMTP.
const fs = require('fs');
const wf = JSON.parse(fs.readFileSync('automation/n8n/dezmos-email-automation.workflow.json','utf8'));
const codeOf = (name) => wf.nodes.find(n => n.name === name).parameters.jsCode;

function parseCsv(text) {
  const rows = []; let row = [], field = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i+1] === '"') { field += '"'; i++; }
      else if (c === '"') q = false;
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else if (c !== '\r') field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const hdr = rows.shift();
  return rows.filter(r => r.some(v => v !== ''))
             .map(r => Object.fromEntries(hdr.map((h,i) => [h, r[i] ?? ''])));
}

const cfgNode = wf.nodes.find(n => n.name === 'Campaign Config');
const cfg = Object.fromEntries(
  cfgNode.parameters.assignments.assignments.map(a => [a.name, a.value])
);
// point paths at the repo for the test
cfg.leadsCsvPath = 'leads/ksfe-trivandrum-branches.csv';
cfg.suppressionPath = 'automation/data/suppression.csv';

const leads = parseCsv(fs.readFileSync(cfg.leadsCsvPath,'utf8'));
const supp  = parseCsv(fs.readFileSync(cfg.suppressionPath,'utf8'));

function makeCtx(templateHtml, overrides = {}) {
  const conf = { ...cfg, ...overrides };
  const store = {
    'Campaign Config':     [{ json: conf }],
    'Leads To Rows':       leads.map(j => ({ json: j })),
    'Suppression To Rows': supp.map(j => ({ json: j })),
    'Template To Text':    [{ json: { templateHtml } }],
  };
  const $ = (name) => ({ first: () => store[name][0], all: () => store[name] });
  return { $, conf };
}

function runAll(code, ctx) {
  return new Function('$', 'console', `${code}`)(ctx.$, { log: () => {} });
}
function runEach(code, ctx, item) {
  return new Function('$', '$json', 'console', `${code}`)(ctx.$, item, { log: () => {} });
}

let fail = 0;
const check = (label, cond, detail='') => {
  console.log(`${cond ? '  PASS' : '  FAIL'}  ${label}${detail ? ' :: ' + detail : ''}`);
  if (!cond) fail++;
};

const buildCode  = codeOf('Build Send List');
const renderCode = codeOf('Render Email');

// ---- Test 1: P0 filter + daily limit -----------------------------------
console.log('\nTest 1 - priorityFilter=P0, dailyLimit=2');
let ctx = makeCtx('x', { priorityFilter: 'P0', dailyLimit: 2 });
let out = runAll(buildCode, ctx);
check('returns 2 items', out.length === 2, `got ${out.length}`);
check('both are Regional Offices',
      out.every(o => /^R\.O\./.test(o.json.branch_name)),
      out.map(o => o.json.branch_name).join(' | '));

// ---- Test 2: P1 filter --------------------------------------------------
console.log('\nTest 2 - priorityFilter=P1, no limit');
ctx = makeCtx('x', { priorityFilter: 'P1', dailyLimit: 0 });
out = runAll(buildCode, ctx);
check('returns 13 P1 branches', out.length === 13, `got ${out.length}`);
check('no RO leaked in', !out.some(o => /^R\.O\./.test(o.json.branch_name)));

// ---- Test 3: suppression list is honoured -------------------------------
console.log('\nTest 3 - suppression');
supp.push({ email: 'rotvm@ksfe.com', reason: 'test', date_added: '2026-08-18' });
ctx = makeCtx('x', { priorityFilter: 'P0', dailyLimit: 0 });
out = runAll(buildCode, ctx);
check('suppressed address removed', out.length === 1, `got ${out.length}`);
check('the survivor is the Rural RO', out[0].json.email === 'roatl@ksfe.com', out[0].json.email);
supp.pop();

// ---- Test 4: template renders, no leftover placeholders -----------------
console.log('\nTest 4 - render Regional Office template');
const tplRO = fs.readFileSync('automation/templates/ksfe-regional-office.html','utf8');
ctx = makeCtx(tplRO, { priorityFilter: 'P0', dailyLimit: 0 });
out = runAll(buildCode, ctx);
let r = runEach(renderCode, ctx, out[0].json);
check('subject personalised', r.json.subject.includes('R.O. Thiruvananthapuram'), r.json.subject);
check('no {{placeholders}} left in html', !/\{\{/.test(r.json.html));
check('sender email present', r.json.html.includes('info@dezmosdigitalmarketing.com'));
check('unsubscribe line present', /unsubscribe/i.test(r.json.html));
check('plain-text alternative built', r.json.text.length > 400, `${r.json.text.length} chars`);
check('no html tags in text part', !/<[a-z]/i.test(r.json.text));
check('rupee entity decoded', r.json.text.includes('INR 38.52'));

// ---- Test 5: branch template with a real P1 branch ----------------------
console.log('\nTest 5 - render branch template');
const tplBR = fs.readFileSync('automation/templates/ksfe-branch-outreach.html','utf8');
ctx = makeCtx(tplBR, { priorityFilter: 'P1', dailyLimit: 0 });
out = runAll(buildCode, ctx);
const kaz = out.find(o => o.json.branch_name === 'Kazhakuttom');
r = runEach(renderCode, ctx, kaz.json);
check('branch name in subject', r.json.subject.includes('Kazhakuttom'), r.json.subject);
check('greets Branch Manager', r.json.html.includes('Branch Manager'));
check('locality derived from address', r.json.html.includes('Gopinath Tower'));
check('region office phrased', r.json.html.includes('TVM Urban Regional Office'));
check('no leftovers', !/\{\{/.test(r.json.html));

// ---- Test 6: malformed email is rejected --------------------------------
console.log('\nTest 6 - malformed address rejected');
leads.push({ branch_code:'999', branch_name:'Bad Row', email:'not-an-email',
             priority:'P0', address:'', region_office:'' });
ctx = makeCtx('x', { priorityFilter: 'P0', dailyLimit: 0 });
out = runAll(buildCode, ctx);
check('bad row dropped', !out.some(o => o.json.branch_name === 'Bad Row'));
leads.pop();

console.log(fail === 0 ? '\nAll checks passed.' : `\n${fail} CHECK(S) FAILED`);
process.exit(fail === 0 ? 0 : 1);
