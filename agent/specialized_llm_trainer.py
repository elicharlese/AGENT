"""
Specialized LLM Fine-Tuning System for AGENT Mode-Specific Training

This module handles fine-tuning specialized LLMs for each of the 12 AGENT modes
using the comprehensive training data we've created.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, 
    Trainer, DataCollatorForLanguageModeling
)
from datasets import Dataset, load_dataset
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SpecializedModelConfig:
    """Configuration for specialized model training"""
    mode_name: str
    base_model: str
    training_data_path: str
    output_dir: str
    max_length: int = 2048
    learning_rate: float = 2e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 250
    logging_steps: int = 50

class SpecializedLLMTrainer:
    """Fine-tune specialized LLMs for each AGENT mode"""
    
    def __init__(self, config_path: str = "config/specialized_training_config.yaml"):
        self.config_path = config_path
        self.training_data_dir = Path("training_data")
        self.models_dir = Path("models/specialized")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Define the 12 specialized modes
        self.modes = [
            "design", "security", "development", "analysis", 
            "communication", "automation", "research", "reasoning",
            "creative", "educational", "diagnostic", "optimization"
        ]
        
        # Track training progress
        self.training_progress = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load training configuration"""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = self._create_default_config()
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default training configuration"""
        return {
            "base_models": {
                "small": "microsoft/DialoGPT-small",
                "medium": "microsoft/DialoGPT-medium", 
                "large": "microsoft/DialoGPT-large",
                "code": "microsoft/CodeGPT-small-py",
                "instruct": "microsoft/DialoGPT-medium"
            },
            "mode_model_mapping": {
                "design": "medium",
                "security": "medium", 
                "development": "code",
                "analysis": "medium",
                "communication": "instruct",
                "automation": "medium",
                "research": "medium",
                "reasoning": "large",
                "creative": "medium",
                "educational": "instruct",
                "diagnostic": "medium",
                "optimization": "medium"
            },
            "training_params": {
                "max_length": 1024,
                "learning_rate": 2e-5,
                "num_epochs": 3,
                "batch_size": 4,
                "gradient_accumulation_steps": 4,
                "warmup_steps": 100,
                "save_steps": 500,
                "eval_steps": 250,
                "logging_steps": 50
            },
            "hardware": {
                "use_gpu": True,
                "mixed_precision": True,
                "gradient_checkpointing": True
            }
        }
    
    def prepare_training_data(self, mode: str) -> Dataset:
        """Prepare training data for a specific mode"""
        logger.info(f"Preparing training data for {mode} mode")
        
        mode_dir = self.training_data_dir / mode
        training_file = mode_dir / "session_1_fundamentals.md"
        
        if not training_file.exists():
            raise FileNotFoundError(f"Training data not found for {mode} mode: {training_file}")
        
        # Read and process training content
        with open(training_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract training examples from markdown content
        training_examples = self._extract_training_examples(content, mode)
        
        # Create dataset
        dataset = Dataset.from_dict({
            "text": training_examples,
            "mode": [mode] * len(training_examples)
        })
        
        logger.info(f"Created dataset with {len(training_examples)} examples for {mode} mode")
        return dataset
    
    def _extract_training_examples(self, content: str, mode: str) -> List[str]:
        """Extract training examples from markdown content"""
        examples = []
        
        # Split content into sections
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract code blocks
            code_blocks = self._extract_code_blocks(section)
            for code_block in code_blocks:
                examples.append(f"Mode: {mode}\nTask: Code implementation\nContent: {code_block}")
            
            # Extract practical exercises
            if "Exercise" in section or "Practical" in section:
                exercise_text = self._clean_text(section)
                examples.append(f"Mode: {mode}\nTask: Practical exercise\nContent: {exercise_text}")
            
            # Extract key concepts
            if any(keyword in section.lower() for keyword in ["principle", "framework", "method", "technique"]):
                concept_text = self._clean_text(section)
                if len(concept_text) > 100:  # Only include substantial content
                    examples.append(f"Mode: {mode}\nTask: Concept explanation\nContent: {concept_text}")
        
        return examples
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown text"""
        code_blocks = []
        lines = text.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_block:
                        code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
        
        return code_blocks
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text for training"""
        # Remove markdown formatting
        text = text.replace('#', '').replace('*', '').replace('`', '')
        # Remove excessive whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    async def fine_tune_mode(self, mode: str) -> Dict[str, Any]:
        """Fine-tune a specialized model for a specific mode"""
        logger.info(f"Starting fine-tuning for {mode} mode")
        
        try:
            # Get model configuration
            model_type = self.config["mode_model_mapping"][mode]
            base_model = self.config["base_models"][model_type]
            
            # Create model configuration
            model_config = SpecializedModelConfig(
                mode_name=mode,
                base_model=base_model,
                training_data_path=str(self.training_data_dir / mode),
                output_dir=str(self.models_dir / f"{mode}_specialized"),
                **self.config["training_params"]
            )
            
            # Prepare training data
            dataset = self.prepare_training_data(mode)
            
            # Split dataset
            train_test = dataset.train_test_split(test_size=0.1)
            train_dataset = train_test['train']
            eval_dataset = train_test['test']
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16 if self.config["hardware"]["mixed_precision"] else torch.float32,
                device_map="auto" if self.config["hardware"]["use_gpu"] else None
            )
            
            # Tokenize datasets
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    truncation=True,
                    padding=True,
                    max_length=model_config.max_length,
                    return_tensors="pt"
                )
            
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            eval_dataset = eval_dataset.map(tokenize_function, batched=True)
            
            # Set up training arguments
            training_args = TrainingArguments(
                output_dir=model_config.output_dir,
                overwrite_output_dir=True,
                num_train_epochs=model_config.num_epochs,
                per_device_train_batch_size=model_config.batch_size,
                per_device_eval_batch_size=model_config.batch_size,
                gradient_accumulation_steps=model_config.gradient_accumulation_steps,
                learning_rate=model_config.learning_rate,
                warmup_steps=model_config.warmup_steps,
                logging_steps=model_config.logging_steps,
                save_steps=model_config.save_steps,
                eval_steps=model_config.eval_steps,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                fp16=self.config["hardware"]["mixed_precision"],
                gradient_checkpointing=self.config["hardware"]["gradient_checkpointing"],
                dataloader_pin_memory=False,
                report_to=None  # Disable wandb/tensorboard for now
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False,
                pad_to_multiple_of=8 if self.config["hardware"]["mixed_precision"] else None
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                tokenizer=tokenizer,
            )
            
            # Start training
            logger.info(f"Beginning training for {mode} mode...")
            train_result = trainer.train()
            
            # Save the model
            trainer.save_model()
            tokenizer.save_pretrained(model_config.output_dir)
            
            # Save training metrics
            metrics = {
                "mode": mode,
                "base_model": base_model,
                "training_loss": train_result.training_loss,
                "training_steps": train_result.global_step,
                "training_time": train_result.metrics.get("train_runtime", 0),
                "eval_loss": trainer.evaluate().get("eval_loss", 0),
                "model_path": model_config.output_dir,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save metrics to file
            metrics_file = Path(model_config.output_dir) / "training_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.training_progress[mode] = metrics
            logger.info(f"Successfully completed fine-tuning for {mode} mode")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error fine-tuning {mode} mode: {str(e)}")
            self.training_progress[mode] = {"error": str(e), "timestamp": datetime.now().isoformat()}
            raise
    
    async def fine_tune_all_modes(self) -> Dict[str, Any]:
        """Fine-tune specialized models for all modes"""
        logger.info("Starting fine-tuning for all specialized modes")
        
        results = {}
        
        for mode in self.modes:
            try:
                logger.info(f"Processing mode: {mode}")
                result = await self.fine_tune_mode(mode)
                results[mode] = result
                
                # Save progress after each mode
                self._save_progress()
                
            except Exception as e:
                logger.error(f"Failed to fine-tune {mode} mode: {str(e)}")
                results[mode] = {"error": str(e)}
                continue
        
        # Generate final report
        report = self._generate_training_report(results)
        
        logger.info("Completed fine-tuning for all modes")
        return report
    
    def _save_progress(self):
        """Save training progress to file"""
        progress_file = self.models_dir / "training_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(self.training_progress, f, indent=2)
    
    def _generate_training_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive training report"""
        successful_modes = [mode for mode, result in results.items() if "error" not in result]
        failed_modes = [mode for mode, result in results.items() if "error" in result]
        
        report = {
            "summary": {
                "total_modes": len(self.modes),
                "successful": len(successful_modes),
                "failed": len(failed_modes),
                "success_rate": len(successful_modes) / len(self.modes) * 100
            },
            "successful_modes": successful_modes,
            "failed_modes": failed_modes,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_file = self.models_dir / "training_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def get_specialized_model_path(self, mode: str) -> Optional[str]:
        """Get the path to a trained specialized model"""
        model_dir = self.models_dir / f"{mode}_specialized"
        if model_dir.exists() and (model_dir / "pytorch_model.bin").exists():
            return str(model_dir)
        return None
    
    def list_available_models(self) -> List[str]:
        """List all available specialized models"""
        available = []
        for mode in self.modes:
            if self.get_specialized_model_path(mode):
                available.append(mode)
        return available

# Example usage and testing
async def main():
    """Example usage of the specialized LLM trainer"""
    trainer = SpecializedLLMTrainer()
    
    # Fine-tune a single mode for testing
    print("Testing fine-tuning for design mode...")
    try:
        result = await trainer.fine_tune_mode("design")
        print(f"Design mode training completed: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # List available models
    available_models = trainer.list_available_models()
    print(f"Available specialized models: {available_models}")

if __name__ == "__main__":
    asyncio.run(main())
