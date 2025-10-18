#!/usr/bin/env python3
"""
Simple evaluation script for RAG system.
Calls /ask endpoint and checks for expected keywords in responses.
"""

import json
import requests
import argparse


def load_questions(path: str):
    """Load evaluation questions from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def call_ask_api(question: str, base_url: str = "http://localhost:8000"):
    """Call the /ask endpoint with a question."""
    try:
        response = requests.post(f"{base_url}/ask", json={"question": question}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def check_keywords(text: str, keywords: list) -> dict:
    """Check if expected keywords appear in text (case-insensitive)."""
    text_lower = text.lower()
    found = []
    missing = []

    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
        else:
            missing.append(keyword)

    return {
        "found": found,
        "missing": missing,
        "score": len(found) / len(keywords) if keywords else 0.0,
    }


def evaluate_single_question(item: dict, base_url: str):
    """Evaluate a single question."""
    question = item["question"]
    expected_keywords = item.get("expected_keywords", [])

    print(f"\nQ: {question}")

    # Call API
    response = call_ask_api(question, base_url)

    if "error" in response:
        print(f"❌ API Error: {response['error']}")
        return {"question": question, "success": False, "error": response["error"]}

    answer = response.get("answer", "")
    sources = response.get("sources", [])

    print(f"A: {answer[:200]}{'...' if len(answer) > 200 else ''}")

    # Check keywords
    keyword_result = check_keywords(answer, expected_keywords)

    print(f"Keywords found: {keyword_result['found']}")
    if keyword_result["missing"]:
        print(f"Keywords missing: {keyword_result['missing']}")
    print(f"Keyword score: {keyword_result['score']:.2f}")
    print(f"Sources: {len(sources)} results")

    return {
        "question": question,
        "answer": answer,
        "keyword_score": keyword_result["score"],
        "keywords_found": keyword_result["found"],
        "keywords_missing": keyword_result["missing"],
        "num_sources": len(sources),
        "success": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG system")
    parser.add_argument("--questions", default="eval/questions.json", help="Questions JSON file")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", help="Save results to JSON file")

    args = parser.parse_args()

    # Load questions
    questions = load_questions(args.questions)
    print(f"Loaded {len(questions)} questions from {args.questions}")

    # Evaluate each question
    results = []
    total_score = 0
    successful_questions = 0

    for item in questions:
        result = evaluate_single_question(item, args.base_url)
        results.append(result)

        if result.get("success"):
            total_score += result["keyword_score"]
            successful_questions += 1

    # Summary
    avg_score = total_score / successful_questions if successful_questions > 0 else 0
    print(f"\n{'='*50}")
    print("EVALUATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total questions: {len(questions)}")
    print(f"Successful: {successful_questions}")
    print(f"Average keyword score: {avg_score:.2f}")
    print(f"Overall success rate: {successful_questions/len(questions):.2f}")

    # Save results if requested
    if args.output:
        output_data = {
            "summary": {
                "total_questions": len(questions),
                "successful": successful_questions,
                "average_score": avg_score,
                "success_rate": successful_questions / len(questions),
            },
            "results": results,
        }

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
