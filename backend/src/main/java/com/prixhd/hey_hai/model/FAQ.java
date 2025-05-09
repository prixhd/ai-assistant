package com.prixhd.hey_hai.model;


import jakarta.persistence.*;
import lombok.Data;


@Entity
@Data
public class FAQ {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String question;

    @Column(length = 1000)
    private String answer;
}
