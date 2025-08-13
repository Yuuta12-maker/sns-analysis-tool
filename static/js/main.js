// Global variables
let engagementChart = null;
let timingChart = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const platformSelect = document.getElementById('platform');
    const usernameHelp = document.getElementById('usernameHelp');
    
    form.addEventListener('submit', handleFormSubmit);
    platformSelect.addEventListener('change', handlePlatformChange);
});

// Handle platform selection change
function handlePlatformChange(event) {
    const platform = event.target.value;
    const usernameHelp = document.getElementById('usernameHelp');
    const usernameInput = document.getElementById('username');
    
    if (platform === 'instagram') {
        usernameHelp.textContent = 'Instagram選択時はデモデータで動作確認できます（APIキー不要）';
        usernameInput.placeholder = '任意のユーザー名（デモ用）';
    } else if (platform === 'twitter') {
        usernameHelp.textContent = 'Twitter API設定が必要です';
        usernameInput.placeholder = '@を除いたユーザー名';
    } else {
        usernameHelp.textContent = '';
        usernameInput.placeholder = '@を除いたユーザー名';
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        platform: formData.get('platform'),
        username: formData.get('username'),
        period: formData.get('period'),
        analysis_types: formData.getAll('analysis_type')
    };
    
    // Validation
    if (!data.platform || !data.username || !data.period) {
        alert('すべての必須項目を入力してください。');
        return;
    }
    
    if (data.analysis_types.length === 0) {
        alert('少なくとも1つの分析項目を選択してください。');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        console.error('分析エラー:', error);
        alert('分析中にエラーが発生しました。APIキーの設定やネットワーク接続を確認してください。');
    } finally {
        hideLoading();
    }
}

// Show loading spinner
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Display analysis results
function displayResults(data) {
    // Update stats
    document.getElementById('totalPosts').textContent = data.stats.total_posts || '-';
    document.getElementById('avgEngagement').textContent = 
        data.stats.avg_engagement ? `${data.stats.avg_engagement.toFixed(2)}%` : '-';
    document.getElementById('totalImpressions').textContent = 
        data.stats.total_impressions ? formatNumber(data.stats.total_impressions) : '-';
    document.getElementById('followerCount').textContent = 
        data.stats.follower_count ? formatNumber(data.stats.follower_count) : '-';
    
    // Create charts
    if (data.engagement_data) {
        createEngagementChart(data.engagement_data);
    }
    
    if (data.timing_data) {
        createTimingChart(data.timing_data);
    }
    
    // Store data for export
    window.currentAnalysisData = data;
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Create engagement chart
function createEngagementChart(data) {
    const ctx = document.getElementById('engagementChart').getContext('2d');
    
    // Destroy existing chart
    if (engagementChart) {
        engagementChart.destroy();
    }
    
    engagementChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'エンゲージメント率',
                data: data.values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    display: true
                }
            }
        }
    });
}

// Create timing chart
function createTimingChart(data) {
    const ctx = document.getElementById('timingChart').getContext('2d');
    
    // Destroy existing chart
    if (timingChart) {
        timingChart.destroy();
    }
    
    timingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '投稿数',
                data: data.values,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Format large numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Export to CSV
function exportToCSV() {
    if (!window.currentAnalysisData) {
        alert('エクスポートするデータがありません。');
        return;
    }
    
    const data = window.currentAnalysisData;
    let csv = 'データ種別,値\n';
    
    // Add stats
    csv += `総投稿数,${data.stats.total_posts || 0}\n`;
    csv += `平均エンゲージメント率,${data.stats.avg_engagement || 0}%\n`;
    csv += `総インプレッション,${data.stats.total_impressions || 0}\n`;
    csv += `フォロワー数,${data.stats.follower_count || 0}\n`;
    
    // Add engagement data
    if (data.engagement_data) {
        csv += '\n日付,エンゲージメント率\n';
        for (let i = 0; i < data.engagement_data.labels.length; i++) {
            csv += `${data.engagement_data.labels[i]},${data.engagement_data.values[i]}\n`;
        }
    }
    
    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `sns_analysis_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Export to Google Sheets
async function exportToGoogleSheets() {
    if (!window.currentAnalysisData) {
        alert('エクスポートするデータがありません。');
        return;
    }
    
    try {
        const response = await fetch('/api/export/sheets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(window.currentAnalysisData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        if (result.success) {
            alert(`Google Sheetsに保存しました: ${result.sheet_url}`);
            window.open(result.sheet_url, '_blank');
        } else {
            throw new Error(result.error || 'Google Sheetsへの保存に失敗しました');
        }
        
    } catch (error) {
        console.error('Google Sheets export error:', error);
        alert('Google Sheetsへの保存中にエラーが発生しました。設定を確認してください。');
    }
}