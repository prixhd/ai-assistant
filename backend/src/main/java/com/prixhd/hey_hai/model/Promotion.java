package com.prixhd.hey_hai.model;

import lombok.Data;
import java.util.Date;

@Data
public class Promotion {
    private String id;
    private String title;
    private String description;
    private Date startDate;
    private Date endDate;
    private double discountPercentage;
    private String[] applicableProductIds;
}