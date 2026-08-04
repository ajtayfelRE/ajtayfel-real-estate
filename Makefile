.PHONY: help

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
	cd infrastructure/terraform/bootstrap && terraform fmt -recursive

validate:
	cd infrastructure/terraform/bootstrap && terraform validate

plan:
	cd infrastructure/terraform/bootstrap && terraform plan

apply:
	cd infrastructure/terraform/bootstrap && terraform apply

clean:
	find . -name ".terraform" -type d -exec rm -rf {} +
	find . -name "*.tfplan" -delete
