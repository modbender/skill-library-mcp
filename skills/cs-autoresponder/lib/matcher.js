#!/usr/bin/env node
/**
 * matcher.js - 의미 기반 FAQ 매칭
 * 간단한 키워드 매칭 (production에서는 embeddings 권장)
 */

const fs = require('fs');

class FAQMatcher {
  constructor(faqPath) {
    this.faqPath = faqPath;
    this.faqs = this.loadFAQs();
  }

  /**
   * FAQ DB 로드
   */
  loadFAQs() {
    if (!fs.existsSync(this.faqPath)) {
      console.warn(`⚠️  FAQ file not found: ${this.faqPath}`);
      return [];
    }

    const content = fs.readFileSync(this.faqPath, 'utf-8');
    return JSON.parse(content);
  }

  /**
   * 고객 문의에 가장 적합한 FAQ 찾기
   * @param {string} message - 고객 문의 메시지
   * @returns {Object|null} { faq, score } 또는 null
   */
  match(message) {
    if (!message || this.faqs.length === 0) {
      return null;
    }

    const normalizedMessage = this.normalize(message);
    let bestMatch = null;
    let bestScore = 0;

    this.faqs.forEach(faq => {
      const score = this.calculateScore(normalizedMessage, faq);
      
      if (score > bestScore) {
        bestScore = score;
        bestMatch = faq;
      }
    });

    if (bestScore === 0) {
      return null;
    }

    return {
      faq: bestMatch,
      score: bestScore
    };
  }

  /**
   * 텍스트 정규화 (소문자, 공백 제거)
   */
  normalize(text) {
    return text.toLowerCase().replace(/\s+/g, '');
  }

  /**
   * FAQ와 메시지 간 점수 계산
   * @param {string} normalizedMessage 
   * @param {Object} faq 
   * @returns {number} 0-1 사이 점수
   */
  calculateScore(normalizedMessage, faq) {
    let matchCount = 0;
    const totalKeywords = faq.keywords.length;

    faq.keywords.forEach(keyword => {
      const normalizedKeyword = this.normalize(keyword);
      
      if (normalizedMessage.includes(normalizedKeyword)) {
        matchCount++;
      }
    });

    if (matchCount === 0) {
      return 0;
    }

    // 1개 매칭 = 0.7, 2개 = 0.85, 3개 이상 = 1.0
    // 키워드가 적어도 하나 매칭되면 높은 점수
    const baseScore = 0.7;
    const bonus = Math.min(matchCount - 1, 2) * 0.15;
    
    return Math.min(baseScore + bonus, 1.0);
  }

  /**
   * 부정 키워드 감지
   * @param {string} message 
   * @param {Array<string>} negativeKeywords 
   * @returns {boolean}
   */
  detectNegative(message, negativeKeywords) {
    const normalized = this.normalize(message);
    
    return negativeKeywords.some(keyword => {
      const normalizedKeyword = this.normalize(keyword);
      return normalized.includes(normalizedKeyword);
    });
  }

  /**
   * 담당자 요청 감지
   * @param {string} message 
   * @param {Array<string>} humanKeywords 
   * @returns {boolean}
   */
  detectHumanRequest(message, humanKeywords) {
    const normalized = this.normalize(message);
    
    return humanKeywords.some(keyword => {
      const normalizedKeyword = this.normalize(keyword);
      return normalized.includes(normalizedKeyword);
    });
  }

  /**
   * 응답 생성 (톤 적용)
   * @param {Object} faq 
   * @param {Object} config 
   * @returns {string}
   */
  generateResponse(faq, config) {
    let response = faq.answer;

    // 서명 추가
    if (config.responseConfig.signOff) {
      response += `\n\n${config.responseConfig.signOff}`;
    }

    // 길이 제한
    const maxLength = config.responseConfig.maxResponseLength || 500;
    if (response.length > maxLength) {
      response = response.substring(0, maxLength - 3) + '...';
    }

    return response;
  }
}

module.exports = FAQMatcher;
