// Global variables
let mainChart = null;
let timingChart = null;
let currentData = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load data if available
    if (window.analysisData) {
        currentData = window.analysisData;
        populateData();
        createCharts();
    }
});

function initializeDashboard() {
    // Set up navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Set up chart period buttons
    const chartBtns = document.querySelectorAll('.chart-btn');
    chartBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            chartBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateChartPeriod(this.dataset.period);
        });
    });
}

function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }
    
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterTable);
    }
    
    // Select all checkbox
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
}

function populateData() {
    if (!currentData) return;
    
    // Update metrics cards
    updateMetricsCards();
    
    // Populate data table
    populateDataTable();
}

function updateMetricsCards() {
    const stats = currentData.stats;
    
    // Update metric values
    const metrics = {
        posts: stats.total_posts || 0,
        engagement: (stats.total_likes + stats.total_comments) || 0,
        clicks: stats.total_comments || 0,
        cost: Math.round((stats.avg_engagement || 0) * 10)
    };
    
    // Update each metric card
    Object.keys(metrics).forEach(key => {
        const card = document.querySelector(`.metric-card.${key} .metric-value`);
        if (card) {
            card.textContent = formatNumber(metrics[key]);
        }
    });
}

function createCharts() {
    createMainChart();
    createTimingChartDashboard();
}

function createMainChart() {
    const ctx = document.getElementById('mainChart');
    if (!ctx || !currentData.engagement_data) return;
    
    // Destroy existing chart
    if (mainChart) {
        mainChart.destroy();
    }
    
    // Prepare data similar to Amazon Ads style
    const labels = currentData.engagement_data.labels || [];
    const data = currentData.engagement_data.values || [];
    
    // Create gradient
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(0, 188, 212, 0.3)');
    gradient.addColorStop(1, 'rgba(0, 188, 212, 0.05)');
    
    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'エンゲージメント',
                data: data,
                borderColor: '#00bcd4',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#00bcd4',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#232f3e',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#00bcd4',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    grid: {
                        color: '#f0f0f0',
                        borderDash: [2, 2]
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        color: '#666',
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function createTimingChartDashboard() {
    const ctx = document.getElementById('timingChart');
    if (!ctx || !currentData.timing_data) return;
    
    // Destroy existing chart
    if (timingChart) {
        timingChart.destroy();
    }
    
    const labels = currentData.timing_data.labels || [];
    const data = currentData.timing_data.values || [];
    
    timingChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.slice(0, 8), // Show top 8 hours
            datasets: [{
                data: data.slice(0, 8),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#232f3e',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#ff9900',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            }
        }
    });
}

function populateDataTable() {
    const tbody = document.getElementById('dataTableBody');
    if (!tbody || !currentData) return;
    
    // Generate sample post data based on current data
    const posts = generatePostData();
    
    tbody.innerHTML = '';
    
    posts.forEach((post, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <input type="checkbox" class="row-checkbox" data-id="${post.id}">
            </td>
            <td>
                <div class="post-preview">
                    <strong>${post.title}</strong>
                    <div style="color: #666; font-size: 12px; margin-top: 4px;">
                        ${post.preview}
                    </div>
                </div>
            </td>
            <td>
                <span class="status-indicator ${post.status}">
                    ${post.status === 'active' ? '配信中' : '一時停止'}
                </span>
            </td>
            <td>${formatNumber(post.engagement)}</td>
            <td>${formatNumber(post.likes)}</td>
            <td>${formatNumber(post.comments)}</td>
            <td>${formatDate(post.date)}</td>
            <td>
                <span style="color: ${post.performance > 50 ? '#28a745' : '#dc3545'}">
                    ${post.performance}%
                </span>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function generatePostData() {
    if (!currentData) return [];
    
    const posts = [];
    const sampleTitles = [
        '商品ターゲティング',
        'キーワード',
        'ブランドキーワード',
        'カテゴリー',
        'オーディエンス',
        'リターゲティング',
        'プロモーション',
        'セール告知',
        '新商品紹介',
        'ユーザー投稿'
    ];
    
    const samplePreviews = [
        '最新の商品を紹介する投稿です',
        'ユーザーエンゲージメントを高める内容',
        'ブランド認知度向上のための投稿',
        'カテゴリー別商品の紹介',
        '特定オーディエンス向けコンテンツ',
        '過去の購入者向けリターゲティング',
        '期間限定プロモーションの告知',
        '大型セールイベントの宣伝',
        '新発売商品の詳細紹介',
        'お客様の声を紹介する投稿'
    ];
    
    for (let i = 0; i < 10; i++) {
        posts.push({
            id: i + 1,
            title: sampleTitles[i],
            preview: samplePreviews[i],
            status: Math.random() > 0.3 ? 'active' : 'paused',
            engagement: Math.floor(Math.random() * 1000) + 100,
            likes: Math.floor(Math.random() * 500) + 50,
            comments: Math.floor(Math.random() * 100) + 10,
            date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
            performance: Math.floor(Math.random() * 100) + 20
        });
    }
    
    return posts;
}

function filterTable() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    
    const rows = document.querySelectorAll('#dataTableBody tr');
    
    rows.forEach(row => {
        const postTitle = row.querySelector('.post-preview strong')?.textContent.toLowerCase() || '';
        const statusElement = row.querySelector('.status-indicator');
        const rowStatus = statusElement?.classList.contains('active') ? 'active' : 'paused';
        
        const matchesSearch = postTitle.includes(searchTerm);
        const matchesStatus = !statusFilter || rowStatus === statusFilter;
        
        row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    });
}

function updateChartPeriod(period) {
    // This would typically reload data for the selected period
    console.log('Updating chart for period:', period);
    // For demo purposes, we'll just refresh the existing chart
    if (mainChart) {
        mainChart.update();
    }
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
}

function formatDate(date) {
    if (!(date instanceof Date)) return '-';
    return date.toLocaleDateString('ja-JP', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions
function refreshData() {
    // Refresh the current data
    window.location.reload();
}

function exportData() {
    if (!currentData) {
        alert('エクスポートするデータがありません。');
        return;
    }
    
    // Create CSV data
    let csv = 'メトリック,値\n';
    csv += `総投稿数,${currentData.stats.total_posts || 0}\n`;
    csv += `総いいね数,${currentData.stats.total_likes || 0}\n`;
    csv += `総コメント数,${currentData.stats.total_comments || 0}\n`;
    csv += `平均エンゲージメント,${currentData.stats.avg_engagement || 0}\n`;
    
    // Add engagement data
    if (currentData.engagement_data && currentData.engagement_data.labels) {
        csv += '\n日付,エンゲージメント\n';
        for (let i = 0; i < currentData.engagement_data.labels.length; i++) {
            csv += `${currentData.engagement_data.labels[i]},${currentData.engagement_data.values[i] || 0}\n`;
        }
    }
    
    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `sns_analysis_dashboard_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Make functions available globally
window.refreshData = refreshData;
window.exportData = exportData;