import React, { useState, useEffect } from "react";
import "./App.css";

function SymptomChecker() {
  const [step, setStep] = useState(1);
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");
  const [mainSymptom, setMainSymptom] = useState("");
  const [refineAnswer, setRefineAnswer] = useState(""); 
  const [finalAnswer, setFinalAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [randomQuestions, setRandomQuestions] = useState([]);
  const [step2Warning, setStep2Warning] = useState(""); // NEW: warning for step 2

  // Step 3 question templates
  const questionTemplates = [
    [
      "Can you describe the nature of the pain? Is it sharp, dull, cramping, or burning?",
      "Have you experienced any other symptoms, such as nausea, vomiting, fever, or changes in bowel movements?",
      "When did the pain start, and have you noticed any activities or foods that seem to trigger or worsen the pain?"
    ],
    [
      "Please explain what kind of pain you are feeling (sharp, dull, cramping, or burning).",
      "Are there any additional symptoms like nausea, vomiting, or fever?",
      "When did the pain begin, and are there any triggers you’ve noticed?"
    ],
    [
      "How would you describe your pain? Sharp, dull, cramping, or burning?",
      "Do you have other symptoms like nausea, vomiting, or fever?",
      "When did the pain start and are there certain foods or activities that make it worse?"
    ]
  ];

  // Pick random questions only when entering Step 3
  // Pick random questions only when entering Step 3 (run once)
    useEffect(() => {
      if (step === 3 && randomQuestions.length === 0) {
        const questions = questionTemplates[Math.floor(Math.random() * questionTemplates.length)];
        setRandomQuestions(questions);
        setRefineAnswer(""); // reset textarea only once
      }
    }, [step, questionTemplates, randomQuestions.length]);

  // Handle Step Flow
  const handleNextStep = async () => {
    if (step === 2) {
      setLoading(true);
      try {
        // Step 2: validate symptom
        const response = await fetch("http://127.0.0.1:8000/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mainSymptom }),
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Show warning inline if symptom is out-of-scope
        if (data.reply && data.reply.includes("trained only on abdominal pain")) {
          setStep2Warning(data.reply);
          setLoading(false);
          return; // do not proceed to Step 3
        }

        // Clear warning if symptom is valid
        setStep2Warning("");
        setStep(3); // proceed to Step 3
      } catch (err) {
        console.error("Error validating symptom:", err);
        setStep2Warning("⚠️ Error checking symptom. Please make sure backend is running.");
      } finally {
        setLoading(false);
      }
      return;
    }

    if (step === 3) {
      setLoading(true);
      try {
        // Step 3: send refineAnswer to backend for final insights
        const response = await fetch("http://127.0.0.1:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ age, sex, mainSymptom, refineAnswer }),
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        setFinalAnswer(data.reply || "❌ Sorry, no insights were returned.");
        setStep(4);
      } catch (err) {
        console.error("Error fetching insights:", err);
        alert("⚠️ Error fetching health insights. Please try again.");
      } finally {
        setLoading(false);
      }
      return;
    }

    // Step 1 → Step 2
    setStep(step + 1);
  };

  return (
    <div className="symptom-checker-container">
      <h1>Symptom <span className="check">Checker</span></h1>
      <div className="checker-box">
        
        {/* Step 1 */}
        {step === 1 && (
          <div>
            <h3>Hey👋 Tell me a little about yourself</h3>
            <label>
              Age:
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                min="0"
                max="120"
                placeholder="Enter your age"
              />
            </label>
            <br />
            <label>
              Sex:
              <select value={sex} onChange={(e) => setSex(e.target.value)}>
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </label>
            <br />
            <button onClick={handleNextStep} disabled={!age || !sex}>
              Next
            </button>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div>
            <h3>Describe Your Symptom</h3>
            <p>For accurate insights, provide detailed descriptions of your symptoms.</p>
            <textarea
              className="symptom-textarea"
              placeholder="Describe Your Symptom"
              value={mainSymptom}
              onChange={(e) => setMainSymptom(e.target.value)}
            ></textarea>
            {/* Inline warning */}
            {step2Warning && <p className="warning">{step2Warning}</p>}
            <br />
            <button onClick={handleNextStep} disabled={!mainSymptom || loading}>
              {loading ? "Validating..." : "Next"}
            </button>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div>
            <h3>Answer the following questions</h3>
            <p>Answer a few questions to refine your symptom analysis.</p>
            <ol>
              {randomQuestions.map((q, idx) => (
                <li key={idx}>{q}</li>
              ))}
            </ol>
            <textarea
              className="symptom-textarea"
              placeholder="Type your answer here..."
              value={refineAnswer}
              onChange={(e) => setRefineAnswer(e.target.value)}
            ></textarea>
            <br />
            <button onClick={handleNextStep} disabled={!refineAnswer || loading}>
              {loading ? "Loading..." : "Get Health Insights"}
            </button>
          </div>
        )}

        {/* Step 4 */}
        {step === 4 && (
          <div>
            <h3>Your Health Insights</h3>
            <div className="final-answer">{finalAnswer}</div>
            <p className="note">⚕️ Insights are retrieved from medical knowledge sources.</p>
            <br />
            <button onClick={() => setStep(1)}>Start Over</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default SymptomChecker;
