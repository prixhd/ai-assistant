package com.prixhd.hey_hai.service;


import com.fasterxml.jackson.databind.ObjectMapper;
import com.prixhd.hey_hai.model.AssistantResponse;
import com.prixhd.hey_hai.model.StoreData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;

@Service
public class AIService {
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    public AIService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    public AssistantResponse processQuery(String query, StoreData storeData) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("query", query);
            requestBody.put("store_data", storeData);

            HttpEntity<Map<String, Object>> request =
                    new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    aiServiceUrl, request, Map.class);

            AssistantResponse assistantResponse = new AssistantResponse();
            assistantResponse.setTextResponse((String) response.getBody().get("text_response"));
            assistantResponse.setAudioUrl((String) response.getBody().get("audio_url"));

            return assistantResponse;
        } catch (Exception e) {
            AssistantResponse errorResponse = new AssistantResponse();
            errorResponse.setTextResponse("Ва, брат, что-то пошло не так. Попробуй еще раз.");
            return errorResponse;
        }
    }
}

