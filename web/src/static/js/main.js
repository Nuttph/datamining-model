$(document).ready(function () {
    // เปิดใช้งานระบบ Search Dropdown
    $('.search-select').select2({
        width: '100%',
        placeholder: "ค้นหาข้อมูล...",
        allowClear: true
    });

    $('#riskForm').on('submit', function (e) {
        e.preventDefault();

        const group = $('#animalGroup').val();
        const symptoms = $('#symptoms').val();

        if (!group) {
            alert("กรุณาเลือกกลุ่มสัตว์ก่อน");
            return;
        }

        $.ajax({
            url: '/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ group: group, symptoms: symptoms }),
            success: function (response) {
                $('#resultArea').removeClass('d-none');
                const score = response.risk_score;

                // อัปเดตสีตามความเสี่ยง
                let color = '#28a745'; // เขียว
                let text = 'ระดับปกติ';

                if (score >= 80) { color = '#dc3545'; text = 'อันตรายมาก (วิกฤต)'; }
                else if (score >= 50) { color = '#fd7e14'; text = 'ควรเฝ้าระวังใกล้ชิด'; }

                $('#riskGauge').text(score + '%').css('color', color);
                $('#riskText').text(text).css('color', color);
            }
        });
    });
});