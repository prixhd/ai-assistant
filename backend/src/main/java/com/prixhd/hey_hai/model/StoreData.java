package com.prixhd.hey_hai.model;

import lombok.Data;

import java.util.Collection;
import java.util.List;

@Data
public class StoreData {
    private String storeName;
    private String storeDescription;
    private List<Product> products;
    private List<Promotion> promotions;
    private List<Collection> collections;
    private String contactInfo;
    private String deliveryInfo;
}
