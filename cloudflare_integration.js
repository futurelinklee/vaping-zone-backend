// ============================================
// Cloudflare Workers 프론트엔드 연동 코드
// 베이핑존 리뷰 생성기와 상품 관리 API 연동
// ============================================

// 백엔드 API URL (Render 배포 후 업데이트)
const BACKEND_API = 'https://vaping-zone-backend.onrender.com';

// ============================================
// 상품 관리 API 함수들
// ============================================

/**
 * 상품 목록 조회
 * @param {string} channel - 채널 (vapingzone/juiceon/kukdae)
 * @returns {Promise<Array>} 상품 목록
 */
async function loadProducts(channel) {
    try {
        const response = await fetch(`${BACKEND_API}/api/products/${channel}`);
        if (!response.ok) throw new Error('상품 로드 실패');
        return await response.json();
    } catch (error) {
        console.error('상품 로드 오류:', error);
        alert('상품 목록을 불러올 수 없습니다: ' + error.message);
        return [];
    }
}

/**
 * 상품 추가
 * @param {string} channel - 채널
 * @param {Object} productData - 상품 데이터
 * @param {string} productData.productNo - 상품번호
 * @param {string} productData.productName - 상품명
 * @param {string} productData.category - 카테고리 (기타/일회용/액상)
 * @returns {Promise<Object>} 추가된 상품 정보
 */
async function addProduct(channel, productData) {
    try {
        const response = await fetch(`${BACKEND_API}/api/products/${channel}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_no: productData.productNo,
                product_name: productData.productName,
                category: productData.category || '기타'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '상품 추가 실패');
        }
        
        const result = await response.json();
        alert('✅ 상품이 추가되었습니다');
        return result;
    } catch (error) {
        console.error('상품 추가 오류:', error);
        alert('❌ 상품 추가 실패: ' + error.message);
        throw error;
    }
}

/**
 * 상품 수정
 * @param {string} channel - 채널
 * @param {string} oldProductNo - 기존 상품번호
 * @param {Object} productData - 수정할 상품 데이터
 * @returns {Promise<Object>} 수정된 상품 정보
 */
async function updateProduct(channel, oldProductNo, productData) {
    try {
        const response = await fetch(`${BACKEND_API}/api/products/${channel}/${oldProductNo}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_no: productData.productNo,
                product_name: productData.productName,
                category: productData.category || '기타'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '상품 수정 실패');
        }
        
        const result = await response.json();
        alert('✅ 상품이 수정되었습니다');
        return result;
    } catch (error) {
        console.error('상품 수정 오류:', error);
        alert('❌ 상품 수정 실패: ' + error.message);
        throw error;
    }
}

/**
 * 상품 삭제
 * @param {string} channel - 채널
 * @param {string} productNo - 삭제할 상품번호
 * @returns {Promise<Object>} 삭제 결과
 */
async function deleteProduct(channel, productNo) {
    if (!confirm(`상품번호 ${productNo}를 삭제하시겠습니까?`)) {
        return { cancelled: true };
    }
    
    try {
        const response = await fetch(`${BACKEND_API}/api/products/${channel}/${productNo}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '상품 삭제 실패');
        }
        
        const result = await response.json();
        alert('✅ 상품이 삭제되었습니다');
        return result;
    } catch (error) {
        console.error('상품 삭제 오류:', error);
        alert('❌ 상품 삭제 실패: ' + error.message);
        throw error;
    }
}

/**
 * 리뷰 생성 및 다운로드
 * @param {string} channel - 채널
 * @param {number} count - 생성할 리뷰 개수
 * @returns {Promise<Object>} 생성 결과
 */
async function generateReviews(channel, count = 10) {
    try {
        const response = await fetch(`${BACKEND_API}/api/generate-reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel: channel, count: count })
        });
        
        if (!response.ok) throw new Error('리뷰 생성 실패');
        
        // 엑셀 파일 다운로드
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `리뷰_${channel}_${Date.now()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert(`✅ ${count}개의 리뷰가 생성되었습니다`);
        return { success: true, message: `${count}개의 리뷰가 생성되었습니다` };
    } catch (error) {
        console.error('리뷰 생성 오류:', error);
        alert('❌ 리뷰 생성 실패: ' + error.message);
        throw error;
    }
}

// ============================================
// UI 통합 함수들
// ============================================

/**
 * 상품 관리 페이지 열기 버튼 추가
 */
function addProductManagementButton() {
    const button = document.createElement('button');
    button.textContent = '🛍️ 상품 관리';
    button.className = 'product-management-btn';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 9999;
        transition: all 0.3s;
    `;
    
    button.onmouseover = () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 20px rgba(0,0,0,0.3)';
    };
    
    button.onmouseout = () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
    };
    
    button.onclick = () => {
        window.open(`${BACKEND_API}/static/index.html`, '_blank');
    };
    
    document.body.appendChild(button);
}

/**
 * 상품 목록 표시
 * @param {string} containerId - 목록을 표시할 컨테이너 ID
 * @param {string} channel - 채널
 */
async function displayProducts(containerId, channel) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`컨테이너를 찾을 수 없습니다: ${containerId}`);
        return;
    }
    
    container.innerHTML = '<div class="loading">⏳ 상품 로딩 중...</div>';
    
    try {
        const products = await loadProducts(channel);
        
        if (products.length === 0) {
            container.innerHTML = '<div class="empty-state">등록된 상품이 없습니다</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="products-grid">
                ${products.map(p => `
                    <div class="product-card">
                        <span class="category-badge category-${p.category || '기타'}">${p.category || '기타'}</span>
                        <div class="product-no">${p.product_no}</div>
                        <div class="product-name">${p.product_name}</div>
                        <div class="product-actions">
                            <button onclick="handleEditProduct('${channel}', '${p.product_no}', '${p.product_name.replace(/'/g, "\\'")}', '${p.category || '기타'}')">✏️ 수정</button>
                            <button onclick="handleDeleteProduct('${channel}', '${p.product_no}')">🗑️ 삭제</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="error-state">❌ 상품을 불러올 수 없습니다: ${error.message}</div>`;
    }
}

/**
 * 카테고리별 통계 계산
 * @param {Array} products - 상품 목록
 * @returns {Object} 카테고리별 통계
 */
function getCategoryStats(products) {
    const stats = {
        total: products.length,
        기타: 0,
        일회용: 0,
        액상: 0
    };
    
    products.forEach(p => {
        const category = p.category || '기타';
        if (stats[category] !== undefined) {
            stats[category]++;
        }
    });
    
    return stats;
}

// ============================================
// 이벤트 핸들러
// ============================================

/**
 * 상품 수정 핸들러
 */
window.handleEditProduct = async function(channel, productNo, productName, category) {
    const newProductNo = prompt('상품번호:', productNo);
    if (newProductNo === null) return;
    
    const newProductName = prompt('상품명:', productName);
    if (newProductName === null) return;
    
    const newCategory = prompt('카테고리 (기타/일회용/액상):', category);
    if (newCategory === null) return;
    
    try {
        await updateProduct(channel, productNo, {
            productNo: newProductNo,
            productName: newProductName,
            category: newCategory
        });
        
        // 목록 새로고침
        window.location.reload();
    } catch (error) {
        // 오류는 updateProduct에서 이미 표시됨
    }
};

/**
 * 상품 삭제 핸들러
 */
window.handleDeleteProduct = async function(channel, productNo) {
    try {
        await deleteProduct(channel, productNo);
        
        // 목록 새로고침
        window.location.reload();
    } catch (error) {
        // 오류는 deleteProduct에서 이미 표시됨
    }
};

// ============================================
// 초기화
// ============================================

/**
 * 페이지 로드 시 자동 실행
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('베이핑존 상품 관리 API 연동 완료');
    
    // 상품 관리 버튼 추가
    addProductManagementButton();
    
    // 초기 상품 목록 로드 (필요한 경우)
    // displayProducts('product-container', 'vapingzone');
});

// ============================================
// Export (모듈 사용 시)
// ============================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadProducts,
        addProduct,
        updateProduct,
        deleteProduct,
        generateReviews,
        displayProducts,
        getCategoryStats,
        addProductManagementButton
    };
}
