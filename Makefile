TF_DIR := infrastructure/terraform/environments/staging

.PHONY: help install dev fmt validate plan apply clean

help:
	@echo ""
	@echo "AJ Tayfel Real Estate"
	@echo ""
	@echo "Available Commands:"
	@echo ""
	@echo " make dev"
	@echo " make install"
	@echo " make fmt"
	@echo " make validate"
	@echo " make plan"
	@echo " make apply"
	@echo " make clean"

install:
	cd website && npm install

dev:
	cd website && npm run dev

fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive

validate:
	terraform -chdir=$(TF_DIR) init -backend=false
	terraform -chdir=$(TF_DIR) validate

plan:
	terraform -chdir=$(TF_DIR) init -backend-config=backend.hcl
	terraform -chdir=$(TF_DIR) plan

apply:
	terraform -chdir=$(TF_DIR) init -backend-config=backend.hcl
	terraform -chdir=$(TF_DIR) apply

clean:
	find . -name ".terraform" -type d -exec rm -rf {} +
	find . -name "*.tfplan" -delete
