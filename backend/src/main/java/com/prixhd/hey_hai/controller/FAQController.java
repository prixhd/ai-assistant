package com.prixhd.hey_hai.controller;

import com.prixhd.hey_hai.model.FAQ;
import com.prixhd.hey_hai.service.FAQService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/faq")
public class FAQController {
    private final FAQService faqService;

    public FAQController(FAQService faqService) {
        this.faqService = faqService;
    }

    @GetMapping
    public ResponseEntity<List<FAQ>> getAllFAQs() {
        return ResponseEntity.ok(faqService.findAllFAQs());
    }

    @GetMapping("/search")
    public ResponseEntity<List<FAQ>> searchFAQs(@RequestParam String keyword) {
        return ResponseEntity.ok(faqService.findFAQByKeyword(keyword));
    }
}