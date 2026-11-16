'use strict';
const input = document.getElementById('payload');
const output = document.getElementById('report');
const status = document.getElementById('status');
const runButton = document.getElementById('run');
const copyButton = document.getElementById('copy');
const downloadButton = document.getElementById('download');
const initialInput = input.value;
let lastReport = null;

document.getElementById('reset').addEventListener('click', () => {
  input.value = initialInput;
  status.textContent = 'Sample restored';
});
runButton.addEventListener('click', async () => {
  runButton.disabled = true;
  status.textContent = 'Processing locally…';
  output.textContent = '';
  copyButton.disabled = true;
  downloadButton.disabled = true;
  try {
    const payload = JSON.parse(input.value);
    if (!payload || Array.isArray(payload) || typeof payload !== 'object') {
      throw new Error('Input must be a JSON object.');
    }
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || ('Request failed (' + response.status + ').'));
    lastReport = result;
    output.textContent = JSON.stringify(result, null, 2);
    status.textContent = 'Completed · Local processing';
    copyButton.disabled = false;
    downloadButton.disabled = false;
  } catch (error) {
    output.textContent = error.message;
    status.textContent = 'Could not complete';
  } finally {
    runButton.disabled = false;
  }
});
copyButton.addEventListener('click', async () => {
  if (!lastReport) return;
  try {
    await navigator.clipboard.writeText(JSON.stringify(lastReport, null, 2));
    status.textContent = 'Report copied';
  } catch {
    status.textContent = 'Clipboard unavailable in this browser';
  }
});
downloadButton.addEventListener('click', () => {
  if (!lastReport) return;
  const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'jarvis-report.json';
  anchor.click();
  URL.revokeObjectURL(url);
});
