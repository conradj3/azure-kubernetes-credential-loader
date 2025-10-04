#!/usr/bin/env python3
"""
Azure Kubernetes Credential Loader

A tool to automatically discover AKS clusters across all Azure subscriptions
and fetch their credentials for kubectl access.
"""

import argparse
import json
import logging
import subprocess
import sys
from typing import List, Dict, Optional, Any, Union
import time


class AKSCredentialLoader:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.setup_logging()

    def setup_logging(self):
        """Configure logging based on verbosity level."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def run_az_command(self, command: List[str], capture_output: bool = True, allow_in_dry_run: bool = False) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Execute an Azure CLI command and return the result."""
        full_command = ['az'] + command

        if self.dry_run and not allow_in_dry_run:
            self.logger.info(f"🔍 Would run: {' '.join(full_command)}")
            return None

        try:
            self.logger.debug(f"Executing: {' '.join(full_command)}")

            if capture_output:
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    parsed_result = json.loads(result.stdout)
                    return parsed_result
                return {}
            else:
                # For commands that don't return JSON (like get-credentials)
                subprocess.run(full_command, check=True, text=True)
                return {}

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(full_command)}")
            self.logger.error(f"Error details: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON output from: {' '.join(full_command)}")
            self.logger.error(f"Parse error: {str(e)}")
            return None

    def run_kubelogin_command(self, command: List[str]) -> bool:
        """Execute a kubelogin command."""
        full_command = ['kubelogin'] + command

        if self.dry_run:
            self.logger.info(f"🔍 Would run: {' '.join(full_command)}")
            return True

        try:
            self.logger.debug(f"Executing: {' '.join(full_command)}")
            subprocess.run(full_command, check=True, text=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Kubelogin command failed: {' '.join(full_command)}")
            self.logger.error(f"Error details: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            return False

    def get_subscriptions(self, subscription_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get list of Azure subscriptions."""
        self.logger.info("🔍 Finding your Azure subscriptions...")

        result = self.run_az_command(['account', 'list'], allow_in_dry_run=True)
        if result is None:
            self.logger.error("❌ Couldn't get your subscriptions")
            return []

        # Ensure we have a list of subscriptions
        subscriptions: List[Dict[str, Any]] = result if isinstance(result, list) else []

        if subscription_filter:
            # Filter subscriptions based on provided IDs
            filtered_subs = [
                sub for sub in subscriptions
                if sub.get('id', '') in subscription_filter or sub.get('name', '') in subscription_filter
            ]
            if not filtered_subs:
                self.logger.warning(f"⚠️ No subscriptions match your filter: {subscription_filter}")
            subscriptions = filtered_subs

        self.logger.info(f"📋 Found {len(subscriptions)} subscription(s)")
        for sub in subscriptions:
            self.logger.info(f"   • {sub.get('name', 'Unknown')}")

        return subscriptions

    def get_aks_clusters(self, subscription_id: str) -> List[Dict[str, Any]]:
        """Get all AKS clusters in a subscription."""
        self.logger.info(f"🔎 Looking for AKS clusters...")

        # Set the subscription context
        if not self.run_az_command(['account', 'set', '--subscription', subscription_id], capture_output=False, allow_in_dry_run=True):
            self.logger.error(f"❌ Can't access this subscription")
            return []

        # Get AKS clusters
        result = self.run_az_command(['aks', 'list'], allow_in_dry_run=True)
        if result is None:
            self.logger.warning(f"⚠️ Couldn't list clusters in this subscription")
            return []

        # Ensure we have a list of clusters
        clusters: List[Dict[str, Any]] = result if isinstance(result, list) else []

        cluster_count = len(clusters)
        if cluster_count == 0:
            self.logger.info(f"📭 No clusters here")
        else:
            self.logger.info(f"🎯 Found {cluster_count} cluster(s):")
            for cluster in clusters:
                self.logger.info(f"     {cluster.get('name', 'Unknown')}")

        return clusters

    def fetch_cluster_credentials(self, subscription_id: str, cluster: Dict[str, Any]) -> bool:
        """Fetch credentials for a single AKS cluster."""
        cluster_name = cluster.get('name', 'Unknown')
        resource_group = cluster.get('resourceGroup', 'Unknown')

        self.logger.info(f"🔑 Getting credentials for: {cluster_name}")

        # Set subscription context
        if not self.run_az_command(['account', 'set', '--subscription', subscription_id], capture_output=False):
            if not self.dry_run:
                self.logger.error(f"❌ Can't switch to subscription")
                return False

        # Get AKS credentials
        get_creds_result = self.run_az_command([
            'aks', 'get-credentials',
            '--resource-group', resource_group,
            '--name', cluster_name,
            '--overwrite-existing'
        ], capture_output=False)

        if get_creds_result is None:
            self.logger.error(f"❌ Failed to get credentials for {cluster_name}")
            return False

        # Convert kubeconfig to use Azure CLI authentication
        if not self.run_kubelogin_command(['convert-kubeconfig', '-l', 'azurecli']):
            self.logger.error(f"❌ kubelogin setup failed for {cluster_name}")
            return False

        self.logger.info(f"✅ Ready: {cluster_name}")
        return True

    def load_all_credentials(self, subscription_filter: Optional[List[str]] = None) -> None:
        """Main method to load credentials for all AKS clusters."""
        self.logger.info("🚀 Starting Azure Kubernetes Credential Loader")

        if self.dry_run:
            self.logger.info("🔍 Preview mode - showing what would be done")

        # Get subscriptions
        subscriptions = self.get_subscriptions(subscription_filter)
        if not subscriptions:
            self.logger.error("❌ No subscriptions found or accessible")
            return

        total_clusters = 0
        successful_clusters = 0

        # Process each subscription
        for subscription in subscriptions:
            subscription_id = subscription.get('id', 'Unknown')
            subscription_name = subscription.get('name', 'Unknown')

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🏢 {subscription_name}")
            self.logger.info(f"{'='*60}")

            # Get clusters in this subscription
            clusters = self.get_aks_clusters(subscription_id)
            total_clusters += len(clusters)

            # Fetch credentials for each cluster
            for cluster in clusters:
                if self.fetch_cluster_credentials(subscription_id, cluster):
                    successful_clusters += 1

                # Small delay to avoid overwhelming Azure API
                if not self.dry_run:
                    time.sleep(1)

        # Summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info("📊 Summary")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Subscriptions: {len(subscriptions)}")
        self.logger.info(f"Clusters found: {total_clusters}")

        if self.dry_run:
            self.logger.info("🔍 Preview completed - no changes made")
        else:
            self.logger.info(f"Configured: {successful_clusters}/{total_clusters}")
            if successful_clusters < total_clusters:
                self.logger.warning(f"⚠️ {total_clusters - successful_clusters} clusters had issues")
            elif successful_clusters > 0:
                self.logger.info(f"🎉 All clusters ready to use!")
            else:
                self.logger.info("📭 No clusters found")


def main():
    parser = argparse.ArgumentParser(
        description="Automatically fetch AKS credentials from all Azure subscriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Process all subscriptions
  %(prog)s --dry-run                # Preview actions without executing
  %(prog)s --subscription sub1 sub2 # Process specific subscriptions
  %(prog)s --verbose                # Enable debug logging
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview actions without executing them'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--subscription', '-s',
        nargs='+',
        help='Process only specific subscription IDs or names'
    )

    args = parser.parse_args()

    # Check prerequisites
    print("🔧 Checking prerequisites...")
    try:
        subprocess.run(['az', '--version'], capture_output=True, check=True)
        print("✅ Azure CLI found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Azure CLI not found - please install it first")
        print("   Install guide: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        sys.exit(1)

    try:
        subprocess.run(['kubelogin', '--version'], capture_output=True, check=True)
        print("✅ kubelogin found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ kubelogin not found - please install it first")
        print("   Install guide: https://github.com/Azure/kubelogin")
        sys.exit(1)

    print("✨ Ready to go!")

    # Create and run the loader
    print("\n" + "="*70)
    print("🚀 Azure Kubernetes Credential Loader")
    print("="*70)

    loader = AKSCredentialLoader(dry_run=args.dry_run, verbose=args.verbose)
    loader.load_all_credentials(subscription_filter=args.subscription)

    print("\n🎉 All done!")
    if not args.dry_run:
        print("\n🔄 What's next:")
        print("   kubectl config get-contexts     # List all contexts")
        print("   kubectl config use-context <name> # Switch to a cluster")


if __name__ == '__main__':
    main()
