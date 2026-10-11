"""解析app_config.yaml文件，生成指定类型的对象"""
from pathlib import Path

from fsspec.config import apply_config
from omegaconf import OmegaConf
from dataclasses import dataclass

# ==================== 日志配置模型 ====================
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    enable: bool
    level: str


@dataclass
class LoggingConfig:
    file: File
    console: Console


# ==================== database配置模型 ====================

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

# ==================== Qdrant 配置模型 ====================

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int


# ==================== Embedding 配置模型 ====================

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


# ==================== ES 配置模型 ====================

@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


# ==================== LLM 配置模型 ====================

@dataclass
class LLMConfig:
    model_name: str
    api_key: str


# ==================== app总配置模型 ====================

@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


#得到yaml配置文件的绝对路径
_yaml_path=Path(__file__).parents[2]/"conf/app_config.yaml"

#根据路径加载配置文件数据-》DictConfig对象
_yaml_data=OmegaConf.load(_yaml_path)
#将数据专黄层AppConfig对象
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(AppConfig,_yaml_data))#使用 AppConfig 这样的 dataclass，可以让配置拥有明确的字段类型和默认值。
#merge 把 AppConfig 中的默认配置和 _yaml_data 中的 YAML 配置合并。如果有相同的配置项，就使用后面的 _yaml_data 覆盖前面的默认值。

if __name__ == "__main__":
    print(app_config)
    print(app_config.logging.console.level)