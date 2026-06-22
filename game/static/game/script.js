document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const balanceEl = document.getElementById('balance');
    const multiplierEl = document.getElementById('multiplier');
    const statusMessageEl = document.getElementById('status-message');
    const betInput = document.getElementById('bet-input');
    const btnHalf = document.getElementById('btn-half');
    const btnDouble = document.getElementById('btn-double');
    const actionBtn = document.getElementById('action-btn');
    const currentProfitEl = document.getElementById('current-profit');
    const historyList = document.getElementById('history-list');

    // Game State
    let balance = 0.00;
    let currentBet = 0;
    let betPlacedForNextRound = false;
    let isCashedOut = false;
    let currentBetId = null;

    // Round State
    let gameState = 'idle'; // idle, flying, crashed
    let currentMultiplier = 1.00;
    let crashPoint = 1.00;
    let animationFrameId = null;
    let startTime = 0;

    // Constants
    const ROUND_DELAY = 5000;
    const API_BASE = window.API_BASE || '';
    const CSRF = window.CSRF_TOKEN || '';

    // Initialize
    fetchUserBalance();
    fetchHistory();
    startIdlePhase();

    // --- API Calls ---

    async function fetchUserBalance() {
        try {
            const res = await fetch(`${API_BASE}/api/user/`);
            if (res.ok) {
                const user = await res.json();
                balance = parseFloat(user.balance);
                updateBalanceDisplay();
            }
        } catch (e) {
            console.error("Failed to fetch balance", e);
        }
    }

    async function fetchHistory() {
        try {
            const res = await fetch(`${API_BASE}/api/history/`);
            if (res.ok) {
                const records = await res.json();
                historyList.innerHTML = '';
                records.reverse().forEach(record => {
                    addHistoryItem(parseFloat(record.multiplier));
                });
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
    }

    // --- Event Listeners ---

    btnHalf.addEventListener('click', () => {
        let val = parseFloat(betInput.value);
        if (isNaN(val)) val = 10;
        betInput.value = Math.max(1, (val / 2)).toFixed(2);
    });

    btnDouble.addEventListener('click', () => {
        let val = parseFloat(betInput.value);
        if (isNaN(val)) val = 10;
        betInput.value = (val * 2).toFixed(2);
    });

    betInput.addEventListener('input', () => {
        let val = parseFloat(betInput.value);
        if (val < 0) betInput.value = '1.00';
    });

    actionBtn.addEventListener('click', handleAction);

    // --- Core Logic ---

    function generateCrashPoint() {
        const e = 100;
        const h = Math.random() * 100;
        if (h < 5) return 1.00;
        let multiplier = Math.floor((e / (e - h)) * 100) / 100;
        return Math.max(1.01, multiplier);
    }

    async function handleAction() {
        if (gameState === 'idle') {
            if (betPlacedForNextRound) {
                alert('Taruhan tidak bisa dibatalkan setelah dipasang.');
            } else {
                let betAmount = parseFloat(betInput.value);
                if (isNaN(betAmount) || betAmount <= 0) return alert('Jumlah taruhan tidak valid.');
                if (betAmount > balance) return alert('Saldo tidak cukup.');

                actionBtn.disabled = true;
                actionBtn.textContent = 'MEMPROSES...';

                try {
                    const res = await fetch(`${API_BASE}/api/bet/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': CSRF
                        },
                        body: JSON.stringify({ bet_amount: betAmount })
                    });

                    const data = await res.json();

                    if (res.ok) {
                        balance = data.new_balance;
                        currentBet = betAmount;
                        currentBetId = data.bet_id;
                        betPlacedForNextRound = true;
                        isCashedOut = false;
                        updateBalanceDisplay();

                        actionBtn.textContent = 'BET TERPASANG';
                        actionBtn.className = 'btn-disabled';
                        actionBtn.disabled = true;
                    } else {
                        alert(data.error || 'Gagal memasang bet.');
                        actionBtn.textContent = 'PASANG BET';
                        actionBtn.className = 'btn-primary';
                        actionBtn.disabled = false;
                    }
                } catch (e) {
                    console.error(e);
                    alert("Kesalahan jaringan. Coba lagi.");
                    actionBtn.textContent = 'PASANG BET';
                    actionBtn.className = 'btn-primary';
                    actionBtn.disabled = false;
                }
            }
        } else if (gameState === 'flying') {
            if (betPlacedForNextRound && !isCashedOut) {
                cashOut();
            }
        }
    }

    async function cashOut() {
        if (!currentBetId) return;

        isCashedOut = true;
        const winnings = currentBet * currentMultiplier;

        currentProfitEl.textContent = `+$${(winnings - currentBet).toFixed(2)}`;
        currentProfitEl.style.color = '#2ecc71';

        actionBtn.textContent = 'CASHED OUT';
        actionBtn.className = 'btn-disabled';
        actionBtn.disabled = true;

        try {
            const res = await fetch(`${API_BASE}/api/cashout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF
                },
                body: JSON.stringify({
                    bet_id: currentBetId,
                    multiplier: currentMultiplier
                })
            });

            const data = await res.json();
            if (res.ok) {
                balance = data.new_balance;
                updateBalanceDisplay();
            }
        } catch (e) {
            console.error("Failed to cashout on backend", e);
        }
    }

    function startIdlePhase() {
        gameState = 'idle';
        document.body.className = 'idle';
        multiplierEl.textContent = '1.00x';
        multiplierEl.classList.remove('crashed');
        statusMessageEl.textContent = 'Menunggu ronde berikutnya...';

        betPlacedForNextRound = false;
        currentBetId = null;
        currentBet = 0;

        actionBtn.textContent = 'PASANG BET';
        actionBtn.className = 'btn-primary';
        actionBtn.disabled = false;

        currentProfitEl.textContent = '$0.00';
        currentProfitEl.style.color = '#2ecc71';

        let timeLeft = ROUND_DELAY / 1000;
        const countdownInterval = setInterval(() => {
            timeLeft--;
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                startGame();
            } else {
                statusMessageEl.textContent = `Mulai dalam ${timeLeft}s...`;
            }
        }, 1000);
        statusMessageEl.textContent = `Mulai dalam ${timeLeft}s...`;
    }

    function startGame() {
        gameState = 'flying';
        document.body.className = 'flying';
        crashPoint = generateCrashPoint();
        currentMultiplier = 1.00;
        startTime = performance.now();

        statusMessageEl.textContent = 'Terbang...';

        if (betPlacedForNextRound && !isCashedOut) {
            actionBtn.textContent = 'CASH OUT';
            actionBtn.className = 'btn-cashout';
            actionBtn.disabled = false;
        } else {
            actionBtn.textContent = 'TUNGGU RONDE BERIKUTNYA';
            actionBtn.className = 'btn-disabled';
            actionBtn.disabled = true;
        }

        function gameLoop(currentTime) {
            if (gameState !== 'flying') return;

            const elapsedTime = (currentTime - startTime) / 1000;
            currentMultiplier = Math.max(1.00, Math.pow(1.06, elapsedTime * 2));

            if (currentMultiplier >= crashPoint) {
                currentMultiplier = crashPoint;
                crashGame();
            } else {
                multiplierEl.textContent = currentMultiplier.toFixed(2) + 'x';

                if (betPlacedForNextRound && !isCashedOut) {
                    currentProfitEl.textContent = `+$${((currentBet * currentMultiplier) - currentBet).toFixed(2)}`;
                }

                animationFrameId = requestAnimationFrame(gameLoop);
            }
        }

        animationFrameId = requestAnimationFrame(gameLoop);
    }

    async function crashGame() {
        gameState = 'crashed';
        document.body.className = 'crashed';

        multiplierEl.textContent = currentMultiplier.toFixed(2) + 'x';
        multiplierEl.classList.add('crashed');
        statusMessageEl.textContent = 'CRASHED!';

        actionBtn.textContent = 'TUNGGU RONDE BERIKUTNYA';
        actionBtn.className = 'btn-disabled';
        actionBtn.disabled = true;

        if (betPlacedForNextRound && !isCashedOut) {
            currentProfitEl.textContent = `-$${currentBet.toFixed(2)}`;
            currentProfitEl.style.color = '#ff4d4d';

            if (currentBetId) {
                try {
                    await fetch(`${API_BASE}/api/crash/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': CSRF
                        },
                        body: JSON.stringify({ bet_id: currentBetId })
                    });
                } catch (e) { console.error(e); }
            }
        }

        addHistoryItem(currentMultiplier);

        setTimeout(() => {
            startIdlePhase();
        }, 3000);
    }

    function updateBalanceDisplay() {
        balanceEl.textContent = balance.toFixed(2);
    }

    function addHistoryItem(multiplier) {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.textContent = multiplier.toFixed(2) + 'x';

        if (multiplier < 1.5) item.classList.add('crash-low');
        else if (multiplier < 5.0) item.classList.add('crash-mid');
        else item.classList.add('crash-high');

        historyList.prepend(item);

        if (historyList.children.length > 15) {
            historyList.removeChild(historyList.lastChild);
        }
    }
});
