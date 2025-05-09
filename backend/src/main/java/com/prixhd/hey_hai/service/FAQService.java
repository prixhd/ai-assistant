package com.prixhd.hey_hai.service;

import com.prixhd.hey_hai.model.FAQ;
import com.prixhd.hey_hai.repository.FAQRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class FAQService {
    private final FAQRepository faqRepository;

    public FAQService(FAQRepository faqRepository) {
        this.faqRepository = faqRepository;
    }

    public List<FAQ> findAllFAQs() {
        return faqRepository.findAll();
    }

    public Optional<FAQ> findFAQById(Long id) {
        return faqRepository.findById(id);
    }

    public List<FAQ> findFAQByKeyword(String keyword) {
        return faqRepository.findByQuestionContainingIgnoreCase(keyword);
    }

    public FAQ saveFAQ(FAQ faq) {
        return faqRepository.save(faq);
    }
}
