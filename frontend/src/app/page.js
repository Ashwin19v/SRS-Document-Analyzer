"use client";
import { useState } from "react";
import {
  Upload,
  Package,
  Clock,
  BarChart,
  AlertTriangle,
  IndianRupee,
  Cpu,
} from "lucide-react";

export default function HomePage() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError("");
      setAnalysis(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to analyze.");
      return;
    }

    setIsLoading(true);
    setError("");
    setAnalysis(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "https://srs-document-analyzer-backend.onrender.com/api/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Something went wrong with the analysis."
        );
      }

      const result = await response.json();
      setAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const Card = ({ icon, title, children }) => (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-300">
      <div className="flex items-center gap-4 mb-4">
        <div className="bg-indigo-100 text-indigo-600 p-3 rounded-lg">
          {icon}
        </div>
        <h3 className="text-xl font-bold text-gray-800">{title}</h3>
      </div>
      <div className="text-gray-600 space-y-2">{children}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <main className="container mx-auto px-4 py-8 md:py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900">
            AI Project Analyzer
          </h1>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your project requirements document (.pdf, .docx, .txt) and
            get an instant, AI-powered analysis of the tech stack, cost, and
            timeline.
          </p>
        </div>

        <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8 border border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="file-upload"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Project Document
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                    >
                      <span>Upload a file</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        className="sr-only"
                        onChange={handleFileChange}
                        accept=".pdf,.docx,.txt"
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    PDF, DOCX, TXT up to 10MB
                  </p>
                </div>
              </div>
              {fileName && (
                <p className="text-center text-sm text-gray-500 mt-2">
                  Selected: {fileName}
                </p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-colors duration-300"
              >
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  "Analyze Project"
                )}
              </button>
            </div>
          </form>
          {error && (
            <p className="mt-4 text-center text-red-600 bg-red-100 p-3 rounded-md">
              {error}
            </p>
          )}
        </div>

        {analysis && (
          <div className="mt-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900">
                {analysis.projectName}
              </h2>
              <p className="mt-2 text-md text-gray-600 max-w-3xl mx-auto">
                {analysis.projectSummary}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Tech Stack */}
              <Card icon={<Package size={24} />} title="Recommended Tech Stack">
                <p>
                  <strong>Frontend:</strong> {analysis.techStack.frontend.name}{" "}
                  <span className="text-sm block text-gray-500">
                    {analysis.techStack.frontend.reason}
                  </span>
                </p>
                <p>
                  <strong>Backend:</strong> {analysis.techStack.backend.name}{" "}
                  <span className="text-sm block text-gray-500">
                    {analysis.techStack.backend.reason}
                  </span>
                </p>
                <p>
                  <strong>Database:</strong> {analysis.techStack.database.name}{" "}
                  <span className="text-sm block text-gray-500">
                    {analysis.techStack.database.reason}
                  </span>
                </p>
                <p>
                  <strong>Deployment:</strong>{" "}
                  {analysis.techStack.deployment.name}{" "}
                  <span className="text-sm block text-gray-500">
                    {analysis.techStack.deployment.reason}
                  </span>
                </p>
              </Card>

              {/* Estimation */}
              <Card
                icon={<BarChart size={24} />}
                title="Effort & Time Estimation"
              >
                <p>
                  <strong>Function Points:</strong>{" "}
                  {analysis.estimation.functionPoints.totalFP} FP{" "}
                  <span className="text-sm block text-gray-500">
                    {analysis.estimation.functionPoints.analysis}
                  </span>
                </p>
                <p>
                  <strong>COCOMO Model:</strong>{" "}
                  {analysis.estimation.cocomo.model} (
                  {analysis.estimation.cocomo.projectType})
                </p>
                <p>
                  <strong>Effort:</strong>{" "}
                  {analysis.estimation.cocomo.effortMonths}
                </p>
                <p>
                  <strong>Timeline:</strong>{" "}
                  {analysis.estimation.cocomo.developmentTimeMonths}
                </p>
                <p>
                  <strong>Team Size:</strong>{" "}
                  {analysis.estimation.cocomo.personnelRequired}
                </p>
              </Card>

              {/* Cost Estimation */}
              <Card
                icon={<IndianRupee size={24} />}
                title="Cost Estimation (INR)"
              >
                <p>
                  <strong>Total Est. Cost:</strong>{" "}
                  <span className="font-bold text-lg">
                    {analysis.costEstimation.totalProjectCost}
                  </span>
                </p>
                <p>
                  <strong>Personnel (Monthly):</strong>{" "}
                  {analysis.costEstimation.personnelCost}
                </p>
                <p>
                  <strong>Infrastructure (Monthly):</strong>{" "}
                  {analysis.costEstimation.infrastructureCost}
                </p>
                <p className="text-sm pt-2 text-gray-500">
                  {analysis.costEstimation.breakdown}
                </p>
              </Card>

              {/* Risk Analysis */}
              <div className="md:col-span-2 lg:col-span-3">
                <Card
                  icon={<AlertTriangle size={24} />}
                  title="Potential Risk Analysis"
                >
                  <ul className="space-y-3 list-disc list-inside">
                    {analysis.riskAnalysis.map((risk, index) => (
                      <li key={index}>
                        <strong>{risk.risk}:</strong> {risk.mitigation}
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
