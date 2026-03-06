"use client";

import { FormEvent, useState } from "react";

import { getClientAuthToken } from "@/lib/auth";
import { getApiBase } from "@/lib/api_base";
import {
  keywordCategoryLabel,
  matchingTypeLabel,
  targetFieldLabel,
} from "@/lib/labels";
import type { KeywordRule } from "@/lib/types";

const API_BASE = getApiBase();

function authHeaders(extra: Record<string, string> = {}) {
  const token = getClientAuthToken() || process.env.NEXT_PUBLIC_API_TOKEN || "";
  const headers: Record<string, string> = { ...extra };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

const CATEGORIES = ["direct", "related", "commercial", "institution_signal", "technical", "negative"];
const MATCHING_TYPES = ["contains", "exact", "fuzzy"];

export function KeywordRuleManager({ initialRules }: { initialRules: KeywordRule[] }) {
  const [rules, setRules] = useState(initialRules);
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState("direct");
  const [weight, setWeight] = useState("3.0");
  const [isNegative, setIsNegative] = useState(false);
  const [matchingType, setMatchingType] = useState("contains");
  const [message, setMessage] = useState<string | null>(null);

  const createRule = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/keyword-rules`, {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          keyword,
          category,
          weight: Number(weight),
          is_negative: isNegative,
          is_active: true,
          matching_type: matchingType,
          target_field: "any",
        }),
      });
      if (!response.ok) throw new Error(`Oluşturma başarısız (${response.status})`);
      const created = (await response.json()) as KeywordRule;
      setRules((prev) => [...prev, created]);
      setKeyword("");
      setMessage("Kural eklendi.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Kural eklenemedi");
    }
  };

  const deleteRule = async (id: number) => {
    const response = await fetch(`${API_BASE}/keyword-rules/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (!response.ok) throw new Error(`Silme başarısız (${response.status})`);
    setRules((prev) => prev.filter((rule) => rule.id !== id));
  };

  const toggleActive = async (rule: KeywordRule) => {
    const response = await fetch(`${API_BASE}/keyword-rules/${rule.id}`, {
      method: "PATCH",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ is_active: !rule.is_active }),
    });
    if (!response.ok) throw new Error(`Güncelleme başarısız (${response.status})`);
    const updated = (await response.json()) as KeywordRule;
    setRules((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
  };

  return (
    <>
      <form className="rule-form" onSubmit={createRule}>
        <input placeholder="Anahtar kelime" value={keyword} onChange={(e) => setKeyword(e.target.value)} required />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((item) => (
            <option key={item} value={item}>
              {keywordCategoryLabel(item)}
            </option>
          ))}
        </select>
        <input value={weight} onChange={(e) => setWeight(e.target.value)} type="number" step="0.1" min="0" required />
        <select value={matchingType} onChange={(e) => setMatchingType(e.target.value)}>
          {MATCHING_TYPES.map((item) => (
            <option key={item} value={item}>
              {matchingTypeLabel(item)}
            </option>
          ))}
        </select>
        <label>
          <input type="checkbox" checked={isNegative} onChange={(e) => setIsNegative(e.target.checked)} /> Negatif
        </label>
        <button type="submit">Kural Ekle</button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Anahtar Kelime</th>
              <th>Kategori</th>
              <th>Ağırlık</th>
              <th>Negatif</th>
              <th>Eşleşme</th>
              <th>Alan</th>
              <th>Aktif</th>
              <th>Sil</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.keyword}</td>
                <td>{keywordCategoryLabel(rule.category)}</td>
                <td>{rule.weight}</td>
                <td>{rule.is_negative ? "Evet" : "Hayır"}</td>
                <td>{matchingTypeLabel(rule.matching_type)}</td>
                <td>{targetFieldLabel(rule.target_field)}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={rule.is_active}
                    onChange={async () => {
                      try {
                        await toggleActive(rule);
                        setMessage("Kural güncellendi.");
                      } catch (error) {
                        setMessage(error instanceof Error ? error.message : "Kural güncellenemedi");
                      }
                    }}
                  />
                </td>
                <td>
                  <button
                    className="danger-btn"
                    onClick={async () => {
                      try {
                        await deleteRule(rule.id);
                        setMessage("Kural silindi.");
                      } catch (error) {
                        setMessage(error instanceof Error ? error.message : "Kural silinemedi");
                      }
                    }}
                  >
                    Sil
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {message ? <p className="table-footer">{message}</p> : null}
    </>
  );
}
