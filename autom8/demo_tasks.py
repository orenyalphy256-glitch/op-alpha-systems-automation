# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

demo_tasks.py - Interactive task demonstration
Run with: python -m autom8.demo_tasks
"""

from autom8.tasks import TaskFactory, run_task


def main():
    print("=" * 60)
    print("AUTOM8 TASK SYSTEM DEMONSTRATION")
    print("=" * 60)

    # List available task types
    print("\n Available task types:")
    for task_type in TaskFactory.list_types():
        print(f"  - {task_type}")

    # Execute each task type
    print("\n Executing tasks...\n")

    for task_type in ["backup", "cleanup", "report"]:
        print(f"\n--- Running {task_type.upper()} task ---")
        result = run_task(task_type)
        print(f"Status: {result['status']}")
        if result["status"] == "success":
            for key, value in result.items():
                if key != "status":
                    print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("All tasks completed. Check logs/system.log for details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
