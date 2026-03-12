$(document).ready(function () {
    // Initialize Select2 for Animal Group
    $('.search-select').select2({
        width: '100%',
        placeholder: "ค้นหาหรือเลือกชนิดสัตว์...",
        allowClear: true,
        dropdownAutoWidth: true
    });

    // --- Symptom Sidebar Logic ---

    // Search functionality
    $('#symptomSearch').on('input', function () {
        const query = $(this).val().toLowerCase();
        $('.symptom-item').each(function () {
            const searchText = $(this).data('search').toLowerCase();
            if (searchText.includes(query)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Handle Checkbox Changes & Update Display
    function updateSelectedSymptoms() {
        const $container = $('#selectedSymptomsDisplay');
        const selected = [];

        $('input[name="symptoms_check"]:checked').each(function () {
            const val = $(this).val();
            const labelTh = $(this).closest('.symptom-item').find('.th').text();
            selected.push({ id: val, text: labelTh });
        });

        if (selected.length === 0) {
            $container.html('<span class="placeholder-text">ยังไม่ได้เลือกอาการ (เลือกได้จากแถบด้านซ้าย)</span>');
        } else {
            $container.empty();
            selected.forEach(item => {
                const $tag = $(`
                    <div class="symptom-tag" data-val="${item.id}">
                        <span>${item.text}</span>
                        <span class="tag-remove">✕</span>
                    </div>
                `);
                $container.append($tag);
            });
        }
    }

    $(document).on('change', 'input[name="symptoms_check"]', function () {
        updateSelectedSymptoms();
    });

    // Remove via Tag
    $(document).on('click', '.tag-remove', function () {
        const val = $(this).parent().data('val');
        $(`input[name="symptoms_check"][value="${val}"]`).prop('checked', false).trigger('change');
    });

    // --- Prediction Logic ---

    let lastScore = 0;

    function animateScore(target) {
        const $el = $('#riskGauge');
        const start = lastScore;
        const duration = 1000;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3);
            const current = (start + (target - start) * ease).toFixed(1);
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
        const r = $circle.attr('r');
        const circumference = 2 * Math.PI * r;

        // Ensure dasharray is set
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
        const symptoms = [];
        $('input[name="symptoms_check"]:checked').each(function () {
            symptoms.push($(this).val());
        });

        const $btn = $('#submitBtn');
        const $resultArea = $('#resultArea');

        if (!group) {
            alert("กรุณาเลือกชนิดสัตว์ก่อน");
            return;
        }

        if (symptoms.length === 0) {
            alert("กรุณาเลือกอาการอย่างน้อย 1 อย่าง");
            return;
        }

        $btn.addClass('loading-pulse').prop('disabled', true).text('⏳ กำลังประมวลผล...');

        const isFirstTime = $resultArea.is(':hidden');

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

                if (score >= 80) {
                    color = '#ef4444'; // Red
                    statusText = '🚨 วิกฤต (Critical Risk)';
                } else if (score >= 65) {
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

                    // If mobile, scroll to result
                    if (isFirstTime && $(window).width() < 1024) {
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