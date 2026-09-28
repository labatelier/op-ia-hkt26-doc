import type { StreamingEvent } from '../types'

/**
 * Decode JWT token and extract the "sub" claim
 *
 * @param token - Encoded JWT access token (`header.payload.signature`).
 * @returns The `sub` claim of the payload, or `'unknown'` when the token is
 * malformed or cannot be decoded.
 */
function extractSubFromToken(token: string): string {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.')
    if (parts.length !== 3) {
      console.warn('[CHAT_SERVICE] Invalid JWT token format')
      return 'unknown'
    }

    // Decode the payload (second part)
    const payload = JSON.parse(atob(parts[1]))
    return payload.sub || 'unknown'
  } catch (error) {
    console.error('[CHAT_SERVICE] Failed to decode JWT token:', error)
    return 'unknown'
  }
}

/**
 * Invoke Bedrock AgentCore endpoint with streaming
 * Returns parsed streaming events as JSON objects
 *
 * Both server-sent events (`data: ` prefixed lines) and bare JSON lines are
 * supported; a `data:` payload that is not valid JSON is yielded as
 * `{ data: <text> }`, and unparseable bare lines are skipped.
 *
 * @param agentArn - ARN of the AgentCore runtime to invoke.
 * @param region - AWS region hosting the runtime.
 * @param sessionId - Value sent as the
 * `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` header.
 * @param bearerToken - Cognito access token; its `sub` claim is sent as the
 * `X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actorid` header.
 * @param prompt - User prompt sent in the request body.
 * @param actorId - Actor identifier sent in the request body as `actor_id`.
 * @returns An async generator yielding the parsed streaming events.
 * @throws Error When the HTTP status is not successful or the response has no
 * body.
 */
export async function* invokeAgentStream(
  agentArn: string,
  region: string,
  sessionId: string,
  bearerToken: string,
  prompt: string,
  actorId: string
): AsyncGenerator<StreamingEvent, void, unknown> {
  const escapedArn = encodeURIComponent(agentArn)
  const url = `https://bedrock-agentcore.${region}.amazonaws.com/runtimes/${escapedArn}/invocations`

  // Extract sub claim from bearer token
  const subClaim = extractSubFromToken(bearerToken)

  const headers = {
    'Authorization': `Bearer ${bearerToken}`,
    'Content-Type': 'application/json',
    'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': sessionId,
    'X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actorid': subClaim,
  }

  const body = JSON.stringify({
    prompt: prompt,
    actor_id: actorId,
  })

  try {
    const response = await fetch(url + '?qualifier=DEFAULT', {
      method: 'POST',
      headers: headers,
      body: body,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
    }

    if (!response.body) {
      throw new Error('Response body is null')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmedLine = line.trim()

        if (trimmedLine === '') {
          continue
        }

        // Handle SSE format (data: prefix)
        if (trimmedLine.startsWith('data: ')) {
          const dataContent = trimmedLine.substring(6).trim()

          // Try to parse as JSON
          try {
            const event = JSON.parse(dataContent) as StreamingEvent
            console.log('[CHAT_SERVICE] Parsed SSE event:', event)
            yield event
          } catch (parseError) {
            // Not JSON, treat as plain text (backward compatibility)
            // Remove quotes that backend might add
            const plainText = dataContent.replace(/^"|"$/g, '')
            console.log('[CHAT_SERVICE] Plain text SSE:', plainText)
            yield { data: plainText } as StreamingEvent
          }
          continue
        }

        // Try to parse as JSON event (no data: prefix)
        try {
          const event = JSON.parse(trimmedLine) as StreamingEvent
          console.log('[CHAT_SERVICE] Parsed JSON event:', event)
          yield event
        } catch (parseError) {
          // If not valid JSON, skip
          console.warn('[CHAT_SERVICE] Failed to parse streaming event:', trimmedLine)
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      try {
        const event = JSON.parse(buffer.trim()) as StreamingEvent
        yield event
      } catch (parseError) {
        // Skip unparseable final buffer
      }
    }
  } catch (error) {
    throw error
  }
}
