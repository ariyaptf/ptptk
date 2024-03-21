document.addEventListener("DOMContentLoaded", function() {
    var bookPrice = document.getElementById('book_price').value;

    var amountRangeInput = document.getElementById('id_amount_contributed');
    var amountDisplay = document.getElementById('id_amount_contributed_helptext');

    var booksRangeInput = document.getElementById('id_number_of_books');
    var booksDisplay = document.getElementById('id_number_of_books_helptext');

    var donate_books = document.getElementById('id_donate_books');

    // ==========================
    // ฟังก์ชันสำหรับอัปเดตจำนวนเงิน
    // ==========================
    function updateAmount(value) {
        if(amountDisplay) {
            // สร้าง object Intl.NumberFormat สำหรับแสดงตัวเลข
            var formatter = new Intl.NumberFormat('en-US', {
                style: 'decimal',
                maximumFractionDigits: 0, // ไม่แสดงทศนิยม
            });
            // อัพเดทข้อความใน amountDisplay ด้วยตัวเลขที่ถูก format
            amountDisplay.textContent = formatter.format(value);
        }
    }
    // ==========================
    // ฟังก์ชันสำหรับอัปเดตจำนวนหนังสือ
    // ==========================
    function updateNumberOfBook(value) {
        if(booksDisplay) {
            // สร้าง object Intl.NumberFormat สำหรับแสดงตัวเลข
            var formatter = new Intl.NumberFormat('en-US', {
                style: 'decimal',
                maximumFractionDigits: 0, // ไม่แสดงทศนิยม
            });
            // อัพเดทข้อความใน booksDisplay ด้วยตัวเลขที่ถูก format
            booksDisplay.textContent = formatter.format(value);
        }
    }
    // ==========================
    // ฟังก์ชันสำหรับตรวสอบยอดหนังสือที่บริจาค
    // ==========================
    function checkDonateAmount() {
        if(donate_books.value > booksRangeInput.value) {
            donate_books.value = booksRangeInput.value;
        }
    }


    // อัพเดทค่าเมื่อโหลดหน้า
    if(amountRangeInput) {
        updateAmount(amountRangeInput.value);

        // อัพเดทค่าเมื่อมีการเปลี่ยนแปลง
        amountRangeInput.addEventListener('input', function() {
            updateAmount(this.value);

            // อัพเดทจำนวนหนังสือ
            if(booksRangeInput) {
                booksRangeInput.value = Math.floor(this.value / bookPrice);
                updateNumberOfBook(booksRangeInput.value);
                checkDonateAmount();
            }
        });
    }
    // อัพเดทค่าเมื่อโหลดหน้า
    if(booksRangeInput) {
        updateNumberOfBook(booksRangeInput.value);

        // อัพเดทค่าเมื่อมีการเปลี่ยนแปลง
        booksRangeInput.addEventListener('input', function() {
            updateNumberOfBook(this.value);
            checkDonateAmount();

            // อัพเดทจำนวนเงิน
            if(amountRangeInput) {
                amountRangeInput.value = this.value * bookPrice;
                updateAmount(amountRangeInput.value);
            }
        });
    }

    // ตรวจสอบจำนวนปันธรรม
    donate_books.addEventListener('input', function() {
        checkDonateAmount();
    });

});
