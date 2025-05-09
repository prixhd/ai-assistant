package com.prixhd.hey_hai.service;

import com.prixhd.hey_hai.model.Product;
import com.prixhd.hey_hai.model.Promotion;
import com.prixhd.hey_hai.model.StoreData;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class StoreService {
    private final Map<String, StoreData> storeCache = new ConcurrentHashMap<>();

    public StoreData getStoreData(String storeId) {
        if (storeCache.containsKey(storeId)) {
            return storeCache.get(storeId);
        }

        StoreData storeData = fetchStoreDataFromExternalService(storeId);
        storeCache.put(storeId, storeData);
        return storeData;
    }

    private StoreData fetchStoreDataFromExternalService(String storeId) {
        // В реальности здесь будет запрос к API магазина
        return createTestStoreData();
    }

    private StoreData createTestStoreData() {
        StoreData data = new StoreData();
        data.setStoreName("Горный Орёл");
        data.setStoreDescription("Лучший магазин Дагестана, валлах! У нас только качественный товар!");
        data.setContactInfo("Тел: +7 (999) 123-45-67");
        data.setDeliveryInfo("Доставка по городу бесплатная от 2000 рублей");

        // Товары
        List<Product> products = new ArrayList<>();

        Product p1 = new Product();
        p1.setId("p1");
        p1.setName("Горный чай");
        p1.setDescription("Настоящий дагестанский чай с горными травами");
        p1.setPrice(350.0);
        p1.setQuantity(100);
        p1.setCategory("Напитки");

        Product p2 = new Product();
        p2.setId("p2");
        p2.setName("Овечий сыр");
        p2.setDescription("Натуральный сыр из овечьего молока");
        p2.setPrice(520.0);
        p2.setQuantity(40);
        p2.setCategory("Еда");

        products.add(p1);
        products.add(p2);

        // Акции
        List<Promotion> promotions = new ArrayList<>();

        Promotion promo1 = new Promotion();
        promo1.setId("promo1");
        promo1.setTitle("Скидка на чай");
        promo1.setDescription("15% на горный чай до конца месяца!");
        promo1.setDiscountPercentage(15.0);
        promo1.setApplicableProductIds(new String[]{"p1"});

        promotions.add(promo1);

        data.setProducts(products);
        data.setPromotions(promotions);

        return data;
    }
}

