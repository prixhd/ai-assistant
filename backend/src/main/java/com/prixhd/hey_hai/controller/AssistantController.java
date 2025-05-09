package com.prixhd.hey_hai.controller;


import com.prixhd.hey_hai.model.AssistantRequest;
import com.prixhd.hey_hai.model.AssistantResponse;
import com.prixhd.hey_hai.model.StoreData;
import com.prixhd.hey_hai.service.AIService;
import com.prixhd.hey_hai.service.StoreService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/assistant")
public class AssistantController {
    private final AIService aiService;
    private final StoreService storeService;

    public AssistantController(AIService aiService, StoreService storeService) {
        this.aiService = aiService;
        this.storeService = storeService;
    }

    @PostMapping("/query")
    public ResponseEntity<AssistantResponse> processQuery(@RequestBody AssistantRequest request) {
        StoreData storeData = storeService.getStoreData(request.getStoreId());
        AssistantResponse response = aiService.processQuery(request.getQuery(), storeData);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/activate")
    public ResponseEntity<String> activateAssistant() {
        return ResponseEntity.ok("ХАЙ");
    }
}

