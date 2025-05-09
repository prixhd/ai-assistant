package com.prixhd.hey_hai.repository;

import com.prixhd.hey_hai.model.FAQ;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface FAQRepository extends JpaRepository<FAQ, Long> {
    @Query("SELECT f FROM FAQ f WHERE LOWER(f.question) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<FAQ> findByQuestionContainingIgnoreCase(String keyword);
}