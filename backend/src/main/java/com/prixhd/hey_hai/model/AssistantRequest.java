package com.prixhd.hey_hai.model;

import lombok.Data;

@Data
public class AssistantRequest {
    private String query;
    private String storeId;
}