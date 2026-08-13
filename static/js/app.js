/* ── Cheap Flight Finder – Frontend ────────────────────────────────────────── */

const API = {
  flights:     '/api/flights',
  checkNow:    '/api/check-now',
  searchPrice: '/api/search-price',
};

// ── Toast ──────────────────────────────────────────────────────────────────
let toastTimer = null;
function showToast(msg, type = 'info') {
  const toast = document.getElementById('toast');
  const toastMsg  = document.getElementById('toastMsg');
  const toastIcon = document.getElementById('toastIcon');
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

  toast.className = `toast ${type}`;
  toastMsg.textContent  = msg;
  toastIcon.textContent = icons[type] || 'ℹ️';

  // Trigger reflow to restart animation
  void toast.offsetWidth;
  toast.classList.add('show');

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 4000);
}

// ── Fetch helpers ──────────────────────────────────────────────────────────
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  return data;
}

// ── Render flight list ─────────────────────────────────────────────────────
function renderFlights(flights) {
  const list   = document.getElementById('flightList');
  const empty  = document.getElementById('emptyState');

  list.innerHTML = '';

  if (!flights || flights.length === 0) {
    list.classList.add('hidden');
    empty.classList.remove('hidden');
    return;
  }

  list.classList.remove('hidden');
  empty.classList.add('hidden');

  flights.forEach(flight => {
    const item = document.createElement('div');
    item.className = 'flight-item';
    item.dataset.id = flight.id;

    const lastPriceHtml = flight.lastPrice
      ? `<div class="flight-last-price">Last checked: <span>₹${parseFloat(flight.lastPrice).toFixed(2)}</span></div>`
      : '';

    item.innerHTML = `
      <div class="flight-route">
        <span>${flight.origin || '---'}</span>
        <span class="route-arrow">→</span>
        <span>${flight.destination || '---'}</span>
      </div>
      <div class="flight-details">
        <div class="flight-date">📅 ${formatDate(flight.date)}</div>
        <div class="flight-threshold">🎯 Alert below ₹${parseFloat(flight.threshold).toFixed(0)}</div>
        ${lastPriceHtml}
      </div>
      <div class="flight-actions">
        <button class="btn-delete" title="Remove" data-id="${flight.id}" aria-label="Delete flight watch">🗑</button>
      </div>
    `;

    list.appendChild(item);
  });

  // Delete button listeners
  list.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteFlight(parseInt(btn.dataset.id, 10)));
  });
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
      weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    });
  } catch { return dateStr; }
}

// ── Load flights ───────────────────────────────────────────────────────────
async function loadFlights() {
  const list = document.getElementById('flightList');
  list.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading your flights...</p>
    </div>`;
  document.getElementById('emptyState').classList.add('hidden');

  const data = await apiFetch(API.flights);
  if (data.success) {
    renderFlights(data.flights);
  } else {
    list.innerHTML = '';
    showToast('Failed to load flights: ' + data.error, 'error');
  }
}

// ── Add flight ─────────────────────────────────────────────────────────────
async function addFlight(origin, destination, threshold, date) {
  const btn = document.getElementById('addBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⏳</span> Adding...';

  const data = await apiFetch(API.flights, {
    method: 'POST',
    body: JSON.stringify({ origin, destination, threshold: parseFloat(threshold), date }),
  });

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon">+</span> Add to Watch List';

  if (data.success) {
    showToast(`✈️ ${origin} → ${destination} added to watch list!`, 'success');
    document.getElementById('addFlightForm').reset();
    hidePriceResult();
    loadFlights();
  } else {
    showToast(data.error || 'Failed to add flight', 'error');
  }
}

// ── Delete flight ──────────────────────────────────────────────────────────
async function deleteFlight(id) {
  const item = document.querySelector(`.flight-item[data-id="${id}"]`);
  if (item) {
    item.style.opacity = '.4';
    item.style.pointerEvents = 'none';
  }

  const data = await apiFetch(`${API.flights}/${id}`, { method: 'DELETE' });

  if (data.success) {
    showToast('Flight removed from watch list', 'info');
    loadFlights();
  } else {
    showToast(data.error || 'Failed to delete flight', 'error');
    if (item) { item.style.opacity = '1'; item.style.pointerEvents = 'auto'; }
  }
}

// ── Check all now ──────────────────────────────────────────────────────────
async function checkAllNow() {
  const btn = document.getElementById('checkAllBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⏳</span> Checking...';

  const data = await apiFetch(API.checkNow, { method: 'POST' });

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon">🔄</span> Check All Now';

  if (data.success) {
    showToast('Price check complete! Alerts sent if any deals found.', 'success');
    loadFlights(); // Refresh to show updated last prices
  } else {
    showToast(data.error || 'Price check failed', 'error');
  }
}

// ── Check current price ────────────────────────────────────────────────────
async function checkCurrentPrice() {
  const origin      = document.getElementById('origin').value.trim().toUpperCase();
  const destination = document.getElementById('destination').value.trim().toUpperCase();
  const date        = document.getElementById('date').value;

  if (!origin || !destination || !date) {
    showToast('Please fill in origin, destination and date first', 'warning');
    return;
  }
  if (origin.length !== 3 || destination.length !== 3) {
    showToast('Origin and destination must be 3-letter IATA codes', 'warning');
    return;
  }

  const btn = document.getElementById('checkPriceBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⏳</span> Searching...';
  hidePriceResult();

  const data = await apiFetch(API.searchPrice, {
    method: 'POST',
    body: JSON.stringify({ origin, destination, date }),
  });

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon">🔍</span> Check Current Price';

  if (data.success && data.result) {
    showPriceResult(data.result);
  } else {
    showToast(data.error || 'No flights found', 'error');
  }
}

function showPriceResult(result) {
  const container = document.getElementById('priceResult');
  const priceEl   = document.getElementById('priceValue');
  const metaEl    = document.getElementById('priceMeta');

  const threshold = parseFloat(document.getElementById('threshold').value || '0');
  const isDeal    = threshold > 0 && result.price < threshold;

  priceEl.textContent = `₹${result.price.toFixed(2)}`;
  metaEl.textContent  = `${result.airline} · ${result.departure ? new Date(result.departure).toLocaleString() : 'N/A'}`;

  container.classList.toggle('deal', isDeal);
  container.classList.remove('hidden');

  if (isDeal) showToast(`🎉 Deal found! ₹${result.price.toFixed(2)} is below your ₹${threshold} threshold!`, 'success');
}

function hidePriceResult() {
  document.getElementById('priceResult').classList.add('hidden');
}

// ── Swap airports ──────────────────────────────────────────────────────────
function swapAirports() {
  const origin      = document.getElementById('origin');
  const destination = document.getElementById('destination');
  [origin.value, destination.value] = [destination.value, origin.value];
  hidePriceResult();
}

// ── Set min date to today ──────────────────────────────────────────────────
function setMinDate() {
  const dateInput = document.getElementById('date');
  const today = new Date().toISOString().split('T')[0];
  dateInput.min = today;
}

// ── Form submit ────────────────────────────────────────────────────────────
document.getElementById('addFlightForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const origin      = document.getElementById('origin').value.trim().toUpperCase();
  const destination = document.getElementById('destination').value.trim().toUpperCase();
  const threshold   = document.getElementById('threshold').value;
  const date        = document.getElementById('date').value;

  if (!origin || !destination || !threshold || !date) {
    showToast('Please fill in all fields', 'warning');
    return;
  }
  await addFlight(origin, destination, threshold, date);
});

// ── Button listeners ───────────────────────────────────────────────────────
document.getElementById('checkPriceBtn').addEventListener('click', checkCurrentPrice);
document.getElementById('checkAllBtn').addEventListener('click', checkAllNow);
document.getElementById('swapBtn').addEventListener('click', swapAirports);

// ── Init ───────────────────────────────────────────────────────────────────
setMinDate();
loadFlights();
