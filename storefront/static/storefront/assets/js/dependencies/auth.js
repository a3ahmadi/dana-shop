// Form step management
let currentStep = 1;
let mobileNumber = '';
let loginMethod = null;
let isForgotPassword = false;

// DOM elements
const stepTitle = document.getElementById('step-title');
const stepDescription = document.getElementById('step-description');
const stepIndicators = document.querySelectorAll('.step-indicator');
const formSteps = document.querySelectorAll('.form-step');
const mobileInput = document.getElementById('mobile');
const maskedMobileElement = document.getElementById('maskedMobile');
const forgotPasswordMobileElement = document.getElementById('forgotPasswordMobile');

// Form click events
document.getElementById('checkMobileBtn').addEventListener('click', checkMobile);
document.getElementById('chooseOtpLogin').addEventListener('click', () => chooseLoginMethod('otp'));
document.getElementById('choosePasswordLogin').addEventListener('click', () => chooseLoginMethod('password'));
document.getElementById('showForgotPasswordStep').addEventListener('click', showForgotPasswordStep);
document.getElementById('showForgotPasswordStep2').addEventListener('click', showForgotPasswordStep);
document.getElementById('backToMethod').addEventListener('click', backToMethod);
document.getElementById('loginWithPassword').addEventListener('click', loginWithPassword);
document.getElementById('backToMobile').addEventListener('click', backToMobile);
document.getElementById('verifyOtpBtn').addEventListener('click', verifyOtp);
document.getElementById('resend-otp-button').addEventListener('click', resendOtp);
document.getElementById('cancelOtp').addEventListener('click', cancelOtp);
document.getElementById('registerAndLogin').addEventListener('click', registerAndLogin);
document.getElementById('backFromForgotPassword').addEventListener('click', backFromForgotPassword);
document.getElementById('requestPasswordReset').addEventListener('click', requestPasswordReset);
document.getElementById('resetPassword').addEventListener('click', resetPassword);

// Input events
mobileInput.addEventListener('input', formatMobileNumber);
document.getElementById('otpCode').addEventListener('input', autoSubmitOtp);
document.getElementById('regPassword').addEventListener('input', checkPasswordComplexity);
document.getElementById('newPassword').addEventListener('input', checkNewPasswordComplexity);


// Change menu items state on click
const navItems = document.querySelectorAll('.nav-item');
navItems.forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        navItems.forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});

// Form functions
function formatMobileNumber(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 0 && !value.startsWith('0')) {
        value = '0' + value;
    }
    if (value.length > 11) {
        value = value.substring(0, 11);
    }
    e.target.value = value;
}

function checkMobile() {
    const mobile = mobileInput.value;

    if (!mobile || !/^09[0-9]{9}$/.test(mobile)) {
        showError('mobile-error', 'شماره موبایل معتبر نیست');
        return;
    }


    mobileNumber = mobile;
    const maskedMobile = mobile.substring(0, 4) + '*****' + mobile.substring(9);
    maskedMobileElement.textContent = maskedMobile;
    forgotPasswordMobileElement.textContent = maskedMobile;

    hideAllErrors();
    goToStep(2);
}

function chooseLoginMethod(method) {
    loginMethod = method;

    if (method === 'otp') {
        // Simulate OTP code sending
        setTimeout(() => {
            goToStep(3);
        }, 1000);
    } else if (method === 'password') {
        document.getElementById('passwordLoginForm').classList.remove('hidden');
        document.getElementById('chooseOtpLogin').classList.add('hidden');
        document.getElementById('choosePasswordLogin').classList.add('hidden');
        document.getElementById('showForgotPasswordStep').classList.add('hidden');
    }
}

function showForgotPasswordStep() {
    isForgotPassword = true;
    goToStep(5);
}

function backToMethod() {
    document.getElementById('passwordLoginForm').classList.add('hidden');
    document.getElementById('chooseOtpLogin').classList.remove('hidden');
    document.getElementById('choosePasswordLogin').classList.remove('hidden');
    document.getElementById('showForgotPasswordStep').classList.remove('hidden');
}

function loginWithPassword() {
    const password = document.getElementById('password').value;

    if (!password) {
        showError('password-error', 'لطفا رمز عبور را وارد کنید');
        return;
    }

    // Simulate successful login
    alert('ورود با موفقیت انجام شد!');
    // Here you can redirect user to main page
}

function backToMobile() {
    goToStep(1);
}

function verifyOtp() {
    const otpCode = document.getElementById('otpCode').value;

    if (!otpCode || otpCode.length !== 4) {
        showError('otp-error', 'کد تایید باید ۴ رقم باشد');
        return;
    }

    hideAllErrors();

    if (isForgotPassword) {
        goToStep(6);
    } else {
        goToStep(4);
    }
}

function resendOtp() {
    // Simulate resending code
    alert('کد تایید جدید ارسال شد');
}

function cancelOtp() {
    if (isForgotPassword) {
        goToStep(5);
    } else {
        goToStep(2);
    }
}

function registerAndLogin() {
    const name = document.getElementById('name').value;
    const family = document.getElementById('family').value;
    const password = document.getElementById('regPassword').value;

    if (!name) {
        showError('name-error', 'لطفا نام خود را وارد کنید');
        return;
    }

    if (!family) {
        showError('family-error', 'لطفا نام خانوادگی خود را وارد کنید');
        return;
    }

    if (!isPasswordStrong(password)) {
        showError('regPassword-error', 'رمز عبور قوی نیست. لطفا شرایط را بررسی کنید');
        return;
    }

    // Simulate successful registration
    alert('ثبت نام با موفقیت انجام شد!');
    // Here you can redirect user to main page
}

function backFromForgotPassword() {
    isForgotPassword = false;
    goToStep(2);
}

function requestPasswordReset() {
    // Simulate password recovery request
    setTimeout(() => {
        goToStep(3);
    }, 1000);
}

function resetPassword() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!isPasswordStrong(newPassword)) {
        showError('newPassword-error', 'رمز عبور قوی نیست. لطفا شرایط را بررسی کنید');
        return;
    }

    if (newPassword !== confirmPassword) {
        showError('confirmPassword-error', 'رمز عبور و تکرار آن مطابقت ندارند');
        return;
    }

    // Simulate successful password change
    alert('رمز عبور با موفقیت تغییر یافت!');
    // Here you can redirect user to main page
}


// Show error
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

// Hide all errors
function hideAllErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.classList.add('hidden');
    });
}
function autoSubmitOtp(e) {
    if (e.target.value.length === 4) {
        verifyOtp();
    }
}

function checkPasswordComplexity() {
    const password = document.getElementById('regPassword').value;
    checkPasswordConditions(
        password,
        'lengthCondition',
        'uppercaseCondition',
        'lowercaseCondition',
        'numberCondition'
    );
}

function checkNewPasswordComplexity() {
    const password = document.getElementById('newPassword').value;
    checkPasswordConditions(
        password,
        'newLengthCondition',
        'newUppercaseCondition',
        'newLowercaseCondition',
        'newNumberCondition'
    );
}

function checkPasswordConditions(password, lengthId, upperId, lowerId, numberId) {
    // Check length
    const lengthCondition = document.getElementById(lengthId);
    if (password.length >= 8) {
        lengthCondition.classList.remove('text-gray-500');
        lengthCondition.classList.add('text-green-600');
        lengthCondition.querySelector('span').textContent = '✓';
    } else {
        lengthCondition.classList.remove('text-green-600');
        lengthCondition.classList.add('text-gray-500');
        lengthCondition.querySelector('span').textContent = '○';
    }

    // Check uppercase letters
    const upperCondition = document.getElementById(upperId);
    if (/[A-Z]/.test(password)) {
        upperCondition.classList.remove('text-gray-500');
        upperCondition.classList.add('text-green-600');
        upperCondition.querySelector('span').textContent = '✓';
    } else {
        upperCondition.classList.remove('text-green-600');
        upperCondition.classList.add('text-gray-500');
        upperCondition.querySelector('span').textContent = '○';
    }

    // Check lowercase letters
    const lowerCondition = document.getElementById(lowerId);
    if (/[a-z]/.test(password)) {
        lowerCondition.classList.remove('text-gray-500');
        lowerCondition.classList.add('text-green-600');
        lowerCondition.querySelector('span').textContent = '✓';
    } else {
        lowerCondition.classList.remove('text-green-600');
        lowerCondition.classList.add('text-gray-500');
        lowerCondition.querySelector('span').textContent = '○';
    }

    // Check numbers
    const numberCondition = document.getElementById(numberId);
    if (/[0-9]/.test(password)) {
        numberCondition.classList.remove('text-gray-500');
        numberCondition.classList.add('text-green-600');
        numberCondition.querySelector('span').textContent = '✓';
    } else {
        numberCondition.classList.remove('text-green-600');
        numberCondition.classList.add('text-gray-500');
        numberCondition.querySelector('span').textContent = '○';
    }
}

function isPasswordStrong(password) {
    return password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[a-z]/.test(password) &&
        /[0-9]/.test(password);
}

function goToStep(step) {
    // Hide all steps
    formSteps.forEach(formStep => {
        formStep.classList.remove('active');
    });

    // Deactivate all indicators
    stepIndicators.forEach(indicator => {
        indicator.classList.remove('active');
    });

    // Show new step
    document.getElementById(`step-${step}`).classList.add('active');

    // Activate new step indicator
    document.querySelector(`.step-indicator[data-step="${step}"]`).classList.add('active');

    // Update title and description
    updateStepTitleAndDescription(step);

    currentStep = step;
}

function updateStepTitleAndDescription(step) {
    const titles = {
        1: 'ورود / ثبت نام',
        2: 'روش ورود را انتخاب کنید',
        3: 'تایید شماره موبایل',
        4: 'تکمیل ثبت نام',
        5: 'بازیابی رمز عبور',
        6: 'تنظیم رمز عبور جدید'
    };

    const descriptions = {
        1: 'برای ثبت نام یا ورود، شماره موبایل خود را وارد کنید',
        2: 'چگونه می‌خواهید وارد شوید؟',
        3: 'کد تایید ارسال شده را وارد کنید',
        4: 'اطلاعات حساب خود را تکمیل کنید',
        5: 'برای بازیابی رمز عبور، شماره موبایل خود را تأیید کنید',
        6: 'رمز عبور جدید خود را تنظیم کنید'
    };

    stepTitle.textContent = titles[step];
    stepDescription.textContent = descriptions[step];
}

function togglePassword(inputId, toggleBtn) {
    const input = document.getElementById(inputId);
    const svg = toggleBtn.querySelector('svg');

    if (input.type === 'password') {
        input.type = 'text';
        // icon eye-slash
        svg.outerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
        </svg>
    `;
    } else {
        input.type = 'password';
        // icon eye
        svg.outerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
    `;
    }
}

// Prevent debugging and inspection
/*
document.addEventListener('contextmenu', (e) => e.preventDefault());
document.addEventListener('keydown', (e) => {
    // Prevent F12 and Ctrl+Shift+I
    if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
        e.preventDefault();
    }
});*/
