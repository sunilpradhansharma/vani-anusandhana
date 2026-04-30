# vāṇī-anusandhāna — system architecture

```mermaid
graph TD

subgraph ING["🔄  Ingestion pipeline — one-time · Apple Silicon · ~12× realtime"]
  YT(["📺 YouTube Playlist<br/>25 → 5,000 lectures<br/>playlist URL only"])
  DL["yt-dlp<br/>audio-only extract<br/>MP3 · best quality · no video"]
  WH["mlx-whisper large-v3<br/>Apple GPU + Neural Engine<br/>Sanskrit initial_prompt · lang=en · temp=0"]
  TR[/"Transcript JSON<br/>full text + timed segments<br/>word-level timestamps"/]
  CH[/"Sentence-aware chunks<br/>~60s windows · 15s overlap<br/>cut at sentence boundary · not mid-word"/]
  SN["Sanskrit normalize<br/>rapidfuzz ≥ 90% · exact + fuzzy<br/>normalization_dict.json · Layer 2 of 3"]
  EM["bge-m3 embed<br/>dense 1024-dim + sparse BM25<br/>embeds text_normalized · batch_size=32"]
  QD[("Qdrant<br/>hybrid vector index<br/>payload: video · timestamps · text")]
end

subgraph QRY["⚡  Query pipeline — real-time · target &lt; 1.5 s end-to-end"]
  DV(["🙏 Devotee asks<br/>natural language question<br/>any Sanskrit spelling accepted"])
  API["FastAPI  /search<br/>POST · JSON · top_k = 4<br/>/health · CORS · models loaded at startup"]
  QE["bge-m3 embed<br/>same model · same vector space<br/>dense + sparse query vectors"]
  QS[("Qdrant hybrid search<br/>dense cosine + sparse BM25<br/>retrieves top-20 candidates")]
  RR["Cross-encoder rerank<br/>bge-reranker-v2-m3<br/>full query text × each chunk · more accurate"]
  MG["Merge adjacent segments<br/>same video · gap &lt; 30 s<br/>avoids near-duplicate results"]
  R4["Top 4 results<br/>YouTube deep-link · ?v=ID&amp;t=Ns<br/>timestamp range · transcript snippet"]
  DV2(["🎧 Devotee listens<br/>jumps to exact moment<br/>teacher's actual words · no paraphrase"])
end

YT    -->|"playlist URL"| DL
DL    -->|"MP3 audio"| WH
WH    -->|"JSON + word timestamps"| TR
TR    -->|"segments"| CH
CH    -->|"~60 s chunks"| SN
SN    -->|"text_normalized"| EM
EM    -->|"dense + sparse vectors"| QD

DV    --> API
API   -->|"query string"| QE
QE    -->|"query vectors"| QS
QS    -->|"top-20 candidates"| RR
RR    -->|"reranked scores"| MG
MG    -->|"merged clips"| R4
R4    --> DV2

QD    -.->|"Persisted on disk"| QS

classDef compute  fill:#DBEAFE,stroke:#1D4ED8,color:#1E3A5F,stroke-width:2px,font-weight:bold
classDef storage  fill:#EDE9FE,stroke:#6D28D9,color:#2E1065,stroke-width:2px,font-weight:bold
classDef quality  fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D,stroke-width:2px,font-weight:bold
classDef data     fill:#D1FAE5,stroke:#059669,color:#064E3B,stroke-width:2px,font-weight:bold
classDef output   fill:#FEF3C7,stroke:#D97706,color:#78350F,stroke-width:2px,font-weight:bold
classDef devotee  fill:#F3F4F6,stroke:#6B7280,color:#1F2937,stroke-width:2px,font-weight:bold

class DL,WH,EM,API,QE compute
class QD,QS storage
class SN,RR,MG quality
class TR,CH data
class R4 output
class YT,DV,DV2 devotee
```

**Color key** — blue: compute steps · purple: vector storage · red: quality/Sanskrit layers · green: data artifacts · amber: output · gray: devotee endpoints
