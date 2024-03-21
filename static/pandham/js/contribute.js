document.addEventListener("DOMContentLoaded", function() {
    // กำหนด bookPrice โดยแปลงค่าที่ได้จาก element เป็นตัวเลข
    var bookPrice = parseInt(document.getElementById('book_price').value, 10);

    var amountRangeInput = document.getElementById('id_amount_contributed');
    var amountDisplay = document.getElementById('id_amount_contributed_helptext');

    var booksRangeInput = document.getElementById('id_number_of_books');
    var booksDisplay = document.getElementById('id_number_of_books_helptext');

    // ฟังก์ชันสำหรับอัปเดตจำนวนเงินและจำนวนหนังสือ
    function updateDisplays() {
        var amount = parseInt(amountRangeInput.value, 10);
        var numberOfBooks = Math.floor(amount / bookPrice); // คำนวณจำนวนหนังสือตามจำนวนเงิน

        // อัปเดต display สำหรับจำนวนเงิน
        amountDisplay.textContent = new Intl.NumberFormat('en-US', {
            style: 'decimal',
            maximumFractionDigits: 0,
        }).format(amount);

        // อัปเดต input และ display สำหรับจำนวนหนังสือ
        booksRangeInput.value = numberOfBooks;
        booksDisplay.textContent = new Intl.NumberFormat('en-US', {
            style: 'decimal',
            maximumFractionDigits: 0,
        }).format(numberOfBooks);
    }

    // อัพเดทค่าเมื่อโหลดหน้าและเมื่อมีการเปลี่ยนแปลง
    if(amountRangeInput && booksRangeInput) {
        updateDisplays(); // อัปเดตเมื่อโหลดหน้า

        // อัปเดตเมื่อมีการเปลี่ยนแปลงจำนวนเงิน
        amountRangeInput.addEventListener('input', updateDisplays);
    }
});
