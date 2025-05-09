package com.prixhd.hey_hai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class HeyHaiApplication {

	public static void main(String[] args) {
		SpringApplication.run(HeyHaiApplication.class, args);
	}
}
