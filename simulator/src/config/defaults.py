"""Default configuration for the simulator: services, namespaces, error patterns, etc."""

DEFAULT_SERVICES = [
    {
        "name": "payment-api",
        "namespace": "production",
        "replicas": 3,
        "healthyReplicas": 3,
        "version": "v2.3.1",
        "dependencies": ["database", "redis", "checkout-service"],
    },
    {
        "name": "checkout-service",
        "namespace": "production",
        "replicas": 2,
        "healthyReplicas": 2,
        "version": "v1.8.0",
        "dependencies": ["payment-api", "inventory-service"],
    },
    {
        "name": "inventory-service",
        "namespace": "production",
        "replicas": 2,
        "healthyReplicas": 2,
        "version": "v1.2.0",
        "dependencies": ["database"],
    },
    {
        "name": "user-service",
        "namespace": "production",
        "replicas": 2,
        "healthyReplicas": 2,
        "version": "v3.0.1",
        "dependencies": ["database", "redis"],
    },
    {
        "name": "api-gateway",
        "namespace": "production",
        "replicas": 3,
        "healthyReplicas": 3,
        "version": "v1.5.0",
        "dependencies": ["payment-api", "checkout-service", "inventory-service", "user-service"],
    },
]

DEFAULT_NODES = [
    {
        "name": "node-1",
        "status": "Ready",
        "conditions": ["Ready: True", "MemoryPressure: False", "DiskPressure: False"],
        "allocatableCpu": "4",
        "allocatableMemory": "16Gi",
        "usedCpu": "2.5",
        "usedMemory": "10Gi",
    },
    {
        "name": "node-2",
        "status": "Ready",
        "conditions": ["Ready: True", "MemoryPressure: False", "DiskPressure: False"],
        "allocatableCpu": "4",
        "allocatableMemory": "16Gi",
        "usedCpu": "1.8",
        "usedMemory": "8Gi",
    },
    {
        "name": "node-3",
        "status": "Ready",
        "conditions": ["Ready: True", "MemoryPressure: False", "DiskPressure: False"],
        "allocatableCpu": "8",
        "allocatableMemory": "32Gi",
        "usedCpu": "3.2",
        "usedMemory": "18Gi",
    },
]

COMMIT_AUTHORS = [
    {"name": "john.doe", "email": "john.doe@company.com"},
    {"name": "jane.smith", "email": "jane.smith@company.com"},
    {"name": "bob.wilson", "email": "bob.wilson@company.com"},
    {"name": "alice.chen", "email": "alice.chen@company.com"},
]

COMMIT_MESSAGE_PATTERNS = [
    "Fix bug in {component}",
    "Increase {resource} for {service}",
    "Add new feature: {feature}",
    "Refactor {component}",
    "Update dependencies",
    "Performance optimization for {operation}",
    "Add logging to {component}",
    "Update configuration for {service}",
]

ERROR_PATTERNS = {
    "oom": [
        "java.lang.OutOfMemoryError: Java heap space",
        "java.lang.OutOfMemoryError: GC overhead limit exceeded",
        "Container exceeded memory limit",
    ],
    "null_pointer": [
        "java.lang.NullPointerException",
        "NullPointerException at com.{service}.{component}",
    ],
    "connection": [
        "Connection pool exhausted",
        "Unable to acquire connection from pool",
        "HikariPool-1 - Connection is not available, request timed out after 30000ms",
        "Redis connection refused",
    ],
    "timeout": [
        "java.net.SocketTimeoutException: Read timed out",
        "Connection timed out after 30000ms",
        "Request timeout after 5000ms",
    ],
    "http": [
        "HTTP 503 Service Unavailable",
        "HTTP 502 Bad Gateway",
        "gRPC UNAVAILABLE: Connection refused",
    ],
    "crash": [
        "Application failed to start",
        "Error creating bean with name",
        "Failed to initialize component",
    ],
    "image_pull": [
        "Failed to pull image: registry.company.com/{service}:{version}",
        "ImagePullBackOff: Back-off pulling image",
        "ErrImagePull: rpc error: code = Unknown",
    ],
}

LOG_MESSAGES_HEALTHY = {
    "INFO": [
        "Processing request for {path}",
        "Successfully completed operation",
        "Health check passed",
        "Cache hit for key {key}",
        "Connection pool stats: active=5, idle=15, total=20",
        "Request processed in {latency}ms",
    ],
    "WARN": [
        "Slow query detected: {query} took {latency}ms",
        "Retry attempt {attempt} for operation {operation}",
        "Connection pool running low: available=3",
    ],
}

API_ENDPOINTS = [
    "/api/payments",
    "/api/orders",
    "/api/users",
    "/api/inventory",
    "/api/checkout",
    "/api/health",
    "/api/products",
]

FILE_PATHS = {
    "payment-api": [
        "src/main/java/com/payment/PaymentProcessor.java",
        "src/main/java/com/payment/PaymentController.java",
        "src/main/java/com/payment/PaymentService.java",
        "src/main/resources/application.yml",
    ],
    "checkout-service": [
        "src/main/java/com/checkout/CheckoutService.java",
        "src/main/java/com/checkout/CartController.java",
        "src/main/java/com/checkout/OrderProcessor.java",
    ],
    "inventory-service": [
        "src/main/java/com/inventory/InventoryService.java",
        "src/main/java/com/inventory/StockController.java",
    ],
    "user-service": [
        "src/main/java/com/user/UserService.java",
        "src/main/java/com/user/AuthController.java",
    ],
    "api-gateway": [
        "src/main/java/com/gateway/GatewayConfig.java",
        "src/main/java/com/gateway/RouteConfig.java",
    ],
}
