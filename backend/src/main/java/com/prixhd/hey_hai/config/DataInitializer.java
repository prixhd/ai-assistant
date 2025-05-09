package com.prixhd.hey_hai.config;


import com.prixhd.hey_hai.model.FAQ;
import com.prixhd.hey_hai.repository.FAQRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {
    @Bean
    public CommandLineRunner initData(FAQRepository faqRepository) {
        return args -> {
            if (faqRepository.count() == 0) {
                FAQ faq1 = new FAQ();
                faq1.setQuestion("Как оформить заказ?");
                faq1.setAnswer("Валлах, брат, заказ оформить просто! Выбирай товар, жми 'В корзину', потом 'Оформить'. Заполняешь данные и ждёшь доставку, красавчик!");

                FAQ faq2 = new FAQ();
                faq2.setQuestion("Как вернуть товар?");
                faq2.setAnswer("Э, зачем возвращать, у нас лучший товар! Но если надо, в течение 14 дней приноси товар с чеком. Деньги вернём, не переживай, брат.");

                faqRepository.save(faq1);
                faqRepository.save(faq2);
            }
        };
    }
}
