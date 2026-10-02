(() => {
    const phoneForm = document.getElementById("authForm");
    const otpForm = document.getElementById("otpForm");
    if (!phoneForm || !otpForm) return;

    const phoneInput = document.getElementById("mobile");
    const otpInput = document.getElementById("otpCode");
    const phoneError = document.getElementById("mobile-error");
    const otpError = document.getElementById("otp-error");
    const requestButton = document.getElementById("checkMobileBtn");
    const verifyButton = document.getElementById("verifyOtpBtn");
    const resendButton = document.getElementById("resend-otp-button");
    const countdown = document.getElementById("resend-countdown");
    const csrfToken = phoneForm.querySelector('[name="csrfmiddlewaretoken"]').value;
    const numerals = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩";
    let phone = "";
    let resendUntil = 0;
    let resendTimer;

    function normalizeDigits(value) {
        return value.replace(/[۰-۹٠-٩]/g, digit => String(numerals.indexOf(digit) % 10));
    }
    function normalizePhone(value) {
        let normalized = normalizeDigits(value).trim().replace(/[\s-]/g, "");
        if (normalized.startsWith("+98")) normalized = "0" + normalized.slice(3);
        else if (normalized.startsWith("0098")) normalized = "0" + normalized.slice(4);
        else if (/^9[0-9]{9}$/.test(normalized)) normalized = "0" + normalized;
        return normalized;
    }
    function showError(element, message) {
        element.textContent = message;
        element.classList.toggle("hidden", !message);
    }
    function showStep(step) {
        document.getElementById("step-1").classList.toggle("active", step === 1);
        document.getElementById("step-2").classList.toggle("active", step === 2);
        document.querySelectorAll(".step-indicator").forEach(indicator => indicator.classList.toggle("active", Number(indicator.dataset.step) <= step));
        document.getElementById("step-title").textContent = step === 1 ? "ورود / ثبت نام" : "کد تأیید";
        document.getElementById("step-description").textContent = step === 1 ? "شماره موبایل خود را وارد کنید تا کد ورود ارسال شود" : "کد شش‌رقمی پیامک‌شده را وارد کنید";
        (step === 1 ? phoneInput : otpInput).focus();
    }
    function updateCountdown() {
        const seconds = Math.max(0, Math.ceil((resendUntil - Date.now()) / 1000));
        countdown.textContent = seconds ? `(${seconds} ثانیه)` : "";
        resendButton.disabled = seconds > 0;
        if (!seconds) clearInterval(resendTimer);
    }
    function startCountdown(seconds) {
        resendUntil = Date.now() + seconds * 1000;
        clearInterval(resendTimer);
        updateCountdown();
        resendTimer = setInterval(updateCountdown, 1000);
    }
    async function post(endpoint, body) {
        const response = await fetch(endpoint, {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json", "Accept": "application/json", "X-CSRFToken": csrfToken },
            body: JSON.stringify(body),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const error = new Error("Request failed");
            error.status = response.status;
            error.data = data;
            throw error;
        }
        return data;
    }
    function errorMessage(error, phase) {
        if (error.status === 429) return "درخواست‌های زیادی ثبت شده است. کمی بعد دوباره تلاش کنید.";
        if (error.status === 503) return "ارسال پیامک فعلاً ممکن نیست. کمی بعد دوباره تلاش کنید.";
        if (error.status === 403) return "نشست شما منقضی شده است. صفحه را تازه‌سازی کنید.";
        if (error.status === 400 && phase === "verify") return "کد نامعتبر یا منقضی شده است. دوباره تلاش کنید.";
        return "ارتباط برقرار نشد. دوباره تلاش کنید.";
    }
    async function requestCode() {
        const number = normalizePhone(phoneInput.value);
        showError(phoneError, "");
        showError(otpError, "");
        if (!/^09[0-9]{9}$/.test(number)) {
            showError(phoneError, "شماره موبایل معتبر وارد کنید.");
            phoneInput.focus();
            return;
        }
        requestButton.disabled = true;
        resendButton.disabled = true;
        try {
            const data = await post("/api/v1/accounts/otp/request/", { phone_number: number });
            phone = number;
            phoneInput.value = number;
            document.getElementById("maskedMobile").textContent = `${number.slice(0, 4)}***${number.slice(-4)}`;
            otpInput.value = "";
            showStep(2);
            startCountdown(data.retry_after || 60);
        } catch (error) {
            showError(phoneError, errorMessage(error, "request"));
        } finally {
            requestButton.disabled = false;
        }
    }
    phoneForm.addEventListener("submit", event => {
        event.preventDefault();
        requestCode();
    });
    otpForm.addEventListener("submit", async event => {
        event.preventDefault();
        showError(otpError, "");
        const code = normalizeDigits(otpInput.value.trim());
        if (!/^[0-9]{6}$/.test(code)) {
            showError(otpError, "کد شش‌رقمی را وارد کنید.");
            otpInput.focus();
            return;
        }
        verifyButton.disabled = true;
        try {
            const data = await post("/api/v1/accounts/otp/verify/", {
                phone_number: phone,
                otp: code,
                next: new URLSearchParams(window.location.search).get("next") || "",
            });
            window.location.assign(data.redirect_url || "/");
        } catch (error) {
            showError(otpError, errorMessage(error, "verify"));
            otpInput.select();
        } finally {
            verifyButton.disabled = false;
        }
    });
    resendButton.addEventListener("click", async () => {
        if (resendButton.disabled || !phone) return;
        showStep(1);
        await requestCode();
    });
    document.getElementById("cancelOtp").addEventListener("click", () => {
        clearInterval(resendTimer);
        otpInput.value = "";
        showError(otpError, "");
        showStep(1);
    });
})();
