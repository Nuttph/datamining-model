$(document).ready(function () {
    // Initialize Select2
    $('.search-select').select2({
        width: '100%',
        placeholder: "ค้นหา...",
        allowClear: true,
        dropdownAutoWidth: true
    });

    // Handle Quick Symptom Chips
    $('.chip').on('click', function () {
        const val = $(this).data('val');
        const $select = $('#symptoms');
        let currentVals = $select.val() || [];

        if (currentVals.includes(val)) {
            currentVals = currentVals.filter(v => v !== val);
            $(this).removeClass('active');
        } else {
            currentVals.push(val);
            $(this).addClass('active');
        }

        $select.val(currentVals).trigger('change');
    });

    // Sync chips if Select2 changes manually
    $('#symptoms').on('change', function () {
        const currentVals = $(this).val() || [];
        $('.chip').each(function () {
            const val = $(this).data('val');
            if (currentVals.includes(val)) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    });

    let lastScore = 0;

    function animateScore(target) {
        const $el = $('#riskGauge');
        const start = lastScore;
        const duration = 1000;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const ease = 1 - Math.pow(1 - progress, 3);
            const current = (start + (target - start) * ease).toFixed(2);
            $el.text(current + '%');

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                lastScore = target;
            }
        }
        requestAnimationFrame(update);
    }

    function updateGauge(percent, color) {
        const $circle = $('.gauge-fill');
        const radius = $circle.attr('r');
        const circumference = 2 * Math.PI * radius;

        $circle.css({
            'stroke-dasharray': circumference,
            'stroke': color
        });

        const offset = circumference - (percent / 100 * circumference);
        $circle.css('stroke-dashoffset', offset);
    }

    $('#riskForm').on('submit', function (e) {
        e.preventDefault();

        const group = $('#animalGroup').val();
        const symptoms = $('#symptoms').val();
        const $btn = $('#submitBtn');
        const $resultArea = $('#resultArea');

        if (!group) {
            alert("กรุณาเลือกชนิดสัตว์ก่อน");
            return;
        }

        $btn.addClass('loading-pulse').prop('disabled', true).text('⏳ กำลังประมวลผล...');

        // Don't fade out if already visible, just smooth transition
        const isFirstTime = $resultArea.is(':hidden');
        if (isFirstTime) {
            $resultArea.hide();
        }

        $.ajax({
            url: '/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ group: group, symptoms: symptoms }),
            success: function (response) {
                const score = response.risk_score;
                const symptomsCount = response.symptoms_analyzed;

                let color = '#10b981'; // Green
                let statusText = '✅ ความเสี่ยงต่ำ (Normal)';

                if (score >= 75) {
                    color = '#ef4444'; // Red
                    statusText = '🚨 วิกฤต (Critical Risk)';
                } else if (score >= 40) {
                    color = '#f59e0b'; // Amber
                    statusText = '🟠 เฝ้าระวัง (Warning)';
                }

                setTimeout(() => {
                    if (isFirstTime) {
                        $resultArea.fadeIn(500);
                        lastScore = 0;
                    }

                    animateScore(score);
                    $('#riskText').text(statusText).css('color', color);
                    $('#analysisDetails').html(`
                        วิเคราะห์ข้อมูลแล้ว ${symptomsCount} อาการ<br>
                    `);

                    updateGauge(score, color);

                    $btn.removeClass('loading-pulse').prop('disabled', false).text('🔮 เริ่มการทำนายความเสี่ยง');

                    if (isFirstTime && $(window).width() < 768) {
                        $('html, body').animate({
                            scrollTop: $resultArea.offset().top - 50
                        }, 500);
                    }
                }, 600);
            },
            error: function (xhr) {
                alert("Error: " + xhr.responseText);
                $btn.removeClass('loading-pulse').prop('disabled', false).text('🔮 เริ่มการทำนายความเสี่ยง');
            }
        });
    });
});