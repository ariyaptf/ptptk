var countdownElement = document.getElementById("countdown");
var resendOTPButton = document.getElementById("resend-otp-btn");

function startCountdown() {
    if (resendOTPButton) {
        var countdown = 60;
        resendOTPButton.disabled = true;
        var interval = setInterval(function() {
            countdown--;
            countdownElement.innerText = countdown + " 🕒";

            if (countdown <= 0) {
                clearInterval(interval);
                countdownElement.innerText = "";
                resendOTPButton.disabled = false;
            }
        }, 1000);
    }
}

function resendOTP() {
    // Add logic to resend OTP here
    startCountdown(); // Start the countdown
}

document.addEventListener("DOMContentLoaded", function() {
    // startCountdown();
})
